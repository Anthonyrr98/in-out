from typing import List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from models.goods import Goods
from models.stock import Stock


class StockService:
    """库存查询与预警服务。"""

    @staticmethod
    def list_stock(
        session: Session,
        keyword: Optional[str] = None,
        only_warning: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[Stock], int]:
        stmt = select(Stock).options(joinedload(Stock.goods))
        if keyword:
            kw = f"%{keyword}%"
            stmt = stmt.join(Stock.goods).where(
                (Goods.code.like(kw)) | (Goods.name.like(kw))
            )

        if only_warning:
            # 通过联表筛选库存预警（当前库存总和 < min_stock）
            sub = (
                select(
                    Stock.goods_id,
                    func.sum(Stock.quantity).label("qty"),
                )
                .group_by(Stock.goods_id)
                .subquery()
            )
            stmt = (
                select(Stock)
                .join(sub, Stock.goods_id == sub.c.goods_id)
                .join(Goods, Goods.id == Stock.goods_id)
                .where(sub.c.qty < Goods.min_stock)
            )

        total = int(session.scalar(select(func.count()).select_from(stmt.subquery())) or 0)
        stmt = (
            stmt.order_by(Stock.goods_id, Stock.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = session.execute(stmt).scalars().all()
        return rows, total

