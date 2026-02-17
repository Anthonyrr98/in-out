from datetime import datetime
from typing import Iterable, List, TypedDict

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.goods import Goods
from models.stock import Stock
from models.stock_in import StockIn, StockInItem


class StockInItemData(TypedDict):
    goods_id: int
    quantity: float
    price: float | None
    batch_no: str | None
    location: str | None


class StockInService:
    """入库业务逻辑。"""

    @staticmethod
    def create_stock_in(
        session: Session,
        order_no: str,
        supplier: str | None,
        date: datetime,
        user_id: int | None,
        items: Iterable[StockInItemData],
        remark: str | None = None,
    ) -> StockIn:
        # 校验单号唯一
        exists = session.scalar(select(StockIn).where(StockIn.order_no == order_no))
        if exists:
            raise ValueError(f"入库单号已存在: {order_no}")

        # 校验商品存在
        goods_ids = {item["goods_id"] for item in items}
        if not goods_ids:
            raise ValueError("入库明细不能为空")
        found_ids = {
            gid
            for (gid,) in session.execute(
                select(Goods.id).where(Goods.id.in_(goods_ids))
            )
        }
        missing = goods_ids - found_ids
        if missing:
            raise ValueError(f"以下商品不存在: {missing}")

        stock_in = StockIn(
            order_no=order_no,
            supplier=supplier,
            date=date,
            user_id=user_id,
            remark=remark,
        )
        session.add(stock_in)
        session.flush()

        for item in items:
            in_item = StockInItem(
                stock_in_id=stock_in.id,
                goods_id=item["goods_id"],
                quantity=item["quantity"],
                price=item.get("price"),
                batch_no=item.get("batch_no"),
                location=item.get("location"),
            )
            session.add(in_item)

            # 更新 / 新增库存
            StockInService._increase_stock(
                session=session,
                goods_id=item["goods_id"],
                quantity=item["quantity"],
                batch_no=item.get("batch_no"),
                location=item.get("location"),
            )

        session.flush()
        return stock_in

    @staticmethod
    def _increase_stock(
        session: Session,
        goods_id: int,
        quantity: float,
        batch_no: str | None,
        location: str | None,
    ) -> None:
        stmt = select(Stock).where(
            Stock.goods_id == goods_id,
            Stock.batch_no.is_(batch_no) if batch_no is None else Stock.batch_no == batch_no,
            Stock.location.is_(location) if location is None else Stock.location == location,
        )
        stock = session.execute(stmt).scalars().first()
        if stock:
            stock.quantity = (stock.quantity or 0) + quantity
        else:
            stock = Stock(
                goods_id=goods_id,
                quantity=quantity,
                batch_no=batch_no,
                location=location,
            )
            session.add(stock)

