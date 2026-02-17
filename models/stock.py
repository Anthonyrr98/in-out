from datetime import date

from sqlalchemy import Column, Integer, ForeignKey, Numeric, String, Date
from sqlalchemy.orm import relationship

from .base import Base


class Stock(Base):
    """库存表。按商品 + 批次 + 库位维度统计数量。"""

    __tablename__ = "stock"

    id = Column(Integer, primary_key=True, autoincrement=True)
    goods_id = Column(Integer, ForeignKey("goods.id"), nullable=False, index=True)
    quantity = Column(Numeric(18, 4), nullable=False, default=0)
    batch_no = Column(String(50), nullable=True, comment="批次号")
    location = Column(String(100), nullable=True, comment="库位")
    expire_date = Column(Date, nullable=True, comment="有效期")

    goods = relationship("Goods", backref="stocks")

    def is_expired(self, today: date | None = None) -> bool:
        if not self.expire_date:
            return False
        today = today or date.today()
        return self.expire_date < today

