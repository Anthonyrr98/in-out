from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, String, Numeric, DateTime
from sqlalchemy.orm import relationship

from .base import Base


class StockFlow(Base):
    """库存流水表：记录每一次入库/出库变动。"""

    __tablename__ = "stock_flow"

    id = Column(Integer, primary_key=True, autoincrement=True)
    goods_id = Column(Integer, ForeignKey("goods.id"), nullable=False, index=True)
    change_type = Column(String(10), nullable=False, comment="in/out")
    change_qty = Column(Numeric(18, 4), nullable=False)
    ref_order_type = Column(String(20), nullable=False, comment="stock_in/stock_out")
    ref_order_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    goods = relationship("Goods")

