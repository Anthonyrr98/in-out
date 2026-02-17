from datetime import datetime
from typing import Iterable, TypedDict

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models.goods import Goods
from models.stock import Stock
from models.stock_out import StockOut, StockOutItem


class StockOutItemData(TypedDict):
    goods_id: int
    quantity: float
    price: float | None
    batch_no: str | None
    location: str | None


class StockOutService:
    """出库业务逻辑。"""

    @staticmethod
    def create_stock_out(
        session: Session,
        order_no: str,
        customer: str | None,
        date: datetime,
        user_id: int | None,
        out_type: str,
        items: Iterable[StockOutItemData],
        remark: str | None = None,
    ) -> StockOut:
        # 校验单号唯一
        exists = session.scalar(select(StockOut).where(StockOut.order_no == order_no))
        if exists:
            raise ValueError(f"出库单号已存在: {order_no}")

        goods_ids = {item["goods_id"] for item in items}
        if not goods_ids:
            raise ValueError("出库明细不能为空")

        found_ids = {
            gid
            for (gid,) in session.execute(
                select(Goods.id).where(Goods.id.in_(goods_ids))
            )
        }
        missing = goods_ids - found_ids
        if missing:
            raise ValueError(f"以下商品不存在: {missing}")

        # 校验库存是否足够（按商品维度汇总）
        for gid in goods_ids:
            total_qty = session.scalar(
                select(func.coalesce(func.sum(Stock.quantity), 0)).where(
                    Stock.goods_id == gid
                )
            ) or 0
            need_qty = sum(item["quantity"] for item in items if item["goods_id"] == gid)
            if need_qty > float(total_qty):
                raise ValueError(f"商品 {gid} 库存不足，需要 {need_qty}，当前 {total_qty}")

        stock_out = StockOut(
            order_no=order_no,
            customer=customer,
            date=date,
            user_id=user_id,
            out_type=out_type,
            remark=remark,
        )
        session.add(stock_out)
        session.flush()

        for item in items:
            out_item = StockOutItem(
                stock_out_id=stock_out.id,
                goods_id=item["goods_id"],
                quantity=item["quantity"],
                price=item.get("price"),
                batch_no=item.get("batch_no"),
                location=item.get("location"),
            )
            session.add(out_item)

            StockOutService._decrease_stock(
                session=session,
                goods_id=item["goods_id"],
                quantity=item["quantity"],
            )

        session.flush()
        return stock_out

    @staticmethod
    def _decrease_stock(
        session: Session,
        goods_id: int,
        quantity: float,
    ) -> None:
        """简单 FIFO：按 id 顺序逐条扣减。"""
        remain = quantity
        stmt = (
            select(Stock)
            .where(Stock.goods_id == goods_id, Stock.quantity > 0)
            .order_by(Stock.id)
        )
        for stock in session.execute(stmt).scalars():
            if remain <= 0:
                break
            can_take = float(stock.quantity)
            if can_take <= remain:
                stock.quantity = 0
                remain -= can_take
            else:
                stock.quantity = can_take - remain
                remain = 0
        if remain > 0:
            # 理论上前面检查过不会出现这个情况，这里只是保护
            raise ValueError(f"库存扣减失败，仍缺少 {remain}")

