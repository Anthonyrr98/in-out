from typing import Iterable

import pandas as pd
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models.goods import Goods
from models.stock import Stock
from models.stock_in import StockIn, StockInItem
from models.stock_out import StockOut, StockOutItem


class ReportService:
    """基础报表导出服务。"""

    @staticmethod
    def export_stock_summary(session: Session, filepath: str) -> None:
        """导出库存汇总表到 Excel。"""
        stmt = (
            select(
                Goods.code,
                Goods.name,
                Goods.category,
                func.coalesce(func.sum(Stock.quantity), 0).label("quantity"),
            )
            .join(Stock, Stock.goods_id == Goods.id, isouter=True)
            .group_by(Goods.id)
            .order_by(Goods.code)
        )
        rows = session.execute(stmt).all()
        df = pd.DataFrame(
            rows, columns=["商品编码", "商品名称", "分类", "库存数量"]
        )
        df.to_excel(filepath, index=False)

    @staticmethod
    def export_inout_detail(
        session: Session,
        filepath: str,
        start_date,
        end_date,
    ) -> None:
        """导出出入库明细表到 Excel。"""
        in_stmt = (
            select(
                StockIn.date,
                StockIn.order_no,
                Goods.code,
                Goods.name,
                StockInItem.quantity,
                StockInItem.price,
                func.literal("入库").label("type"),
            )
            .join(StockInItem, StockInItem.stock_in_id == StockIn.id)
            .join(Goods, Goods.id == StockInItem.goods_id)
            .where(StockIn.date.between(start_date, end_date))
        )
        out_stmt = (
            select(
                StockOut.date,
                StockOut.order_no,
                Goods.code,
                Goods.name,
                -StockOutItem.quantity,
                StockOutItem.price,
                func.literal("出库").label("type"),
            )
            .join(StockOutItem, StockOutItem.stock_out_id == StockOut.id)
            .join(Goods, Goods.id == StockOutItem.goods_id)
            .where(StockOut.date.between(start_date, end_date))
        )
        rows = list(session.execute(in_stmt)) + list(session.execute(out_stmt))
        df = pd.DataFrame(
            rows, columns=["日期", "单号", "商品编码", "商品名称", "数量", "单价", "类型"]
        )
        df.sort_values(by="日期", inplace=True)
        df.to_excel(filepath, index=False)

