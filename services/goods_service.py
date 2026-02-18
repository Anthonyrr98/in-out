from typing import List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models.goods import Goods
from .base import get_session


class GoodsService:
    """商品表的增删改查服务。"""

    def __init__(self, session: Session | None = None) -> None:
        # 可注入会话，便于测试；默认使用上下文管理器创建
        self._session = session

    def _get_session(self) -> Session:
        if self._session is None:
            raise RuntimeError("This method requires context-managed session")
        return self._session

    # ---------- 上下文管理用法 ----------
    def with_session(self) -> "GoodsService":
        """返回绑定新 Session 的 service，一般在 get_session() 内使用。"""
        return GoodsService()

    # ---------- 具体操作 ----------
    @staticmethod
    def create(
        session: Session,
        code: str,
        name: str,
        category: Optional[str] = None,
        spec: Optional[str] = None,
        unit: Optional[str] = None,
        buy_price: Optional[float] = None,
        sell_price: Optional[float] = None,
        min_stock: Optional[float] = None,
        remark: Optional[str] = None,
    ) -> Goods:
        exists = session.scalar(select(Goods).where(Goods.code == code))
        if exists:
            raise ValueError(f"商品编码已存在: {code}")
        goods = Goods(
            code=code,
            name=name,
            category=category,
            spec=spec,
            unit=unit,
            buy_price=buy_price,
            sell_price=sell_price,
            min_stock=min_stock,
            remark=remark,
        )
        session.add(goods)
        session.flush()
        return goods

    @staticmethod
    def update(
        session: Session,
        goods_id: int,
        **fields,
    ) -> Goods:
        goods = session.get(Goods, goods_id)
        if not goods:
            raise ValueError("商品不存在")
        if "code" in fields:
            new_code = fields["code"]
            exists = session.scalar(
                select(Goods).where(Goods.code == new_code, Goods.id != goods_id)
            )
            if exists:
                raise ValueError(f"商品编码已存在: {new_code}")
        for key, value in fields.items():
            if hasattr(goods, key):
                setattr(goods, key, value)
        session.flush()
        return goods

    @staticmethod
    def delete(session: Session, goods_id: int) -> None:
        goods = session.get(Goods, goods_id)
        if not goods:
            return
        # 逻辑删除，避免破坏已有单据和库存
        goods.is_active = False
        session.flush()

    @staticmethod
    def list(
        session: Session,
        keyword: Optional[str] = None,
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[Goods], int]:
        """返回 (数据列表, 总条数)。"""
        stmt = select(Goods).where(Goods.is_active.is_(True))
        count_stmt = select(func.count()).select_from(Goods).where(Goods.is_active.is_(True))
        if keyword:
            kw = f"%{keyword}%"
            stmt = stmt.where((Goods.code.like(kw)) | (Goods.name.like(kw)))
            count_stmt = count_stmt.where((Goods.code.like(kw)) | (Goods.name.like(kw)))
        if category:
            stmt = stmt.where(Goods.category == category)
            count_stmt = count_stmt.where(Goods.category == category)

        total = int(session.scalar(count_stmt) or 0)

        stmt = (
            stmt.order_by(Goods.code)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = session.execute(stmt).scalars().all()
        return rows, total

