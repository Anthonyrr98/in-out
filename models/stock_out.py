from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric,
    Text,
)
from sqlalchemy.orm import relationship

from .base import Base


class StockOut(Base):
    """出库单主表。"""

    __tablename__ = "stock_out"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(50), nullable=False, unique=True, index=True, comment="出库单号")
    customer = Column(String(200), nullable=True, comment="客户")
    date = Column(DateTime, nullable=False, default=datetime.now, comment="出库日期")
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True, comment="操作员用户ID")
    out_type = Column(String(20), nullable=False, default="sale", comment="出库类型：sale/use/scrap 等")
    remark = Column(Text, nullable=True)

    user = relationship("User", backref="stock_out_orders")
    items = relationship("StockOutItem", back_populates="stock_out", cascade="all, delete-orphan")


class StockOutItem(Base):
    """出库单明细表。"""

    __tablename__ = "stock_out_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_out_id = Column(Integer, ForeignKey("stock_out.id"), nullable=False, index=True)
    goods_id = Column(Integer, ForeignKey("goods.id"), nullable=False, index=True)
    quantity = Column(Numeric(18, 4), nullable=False)
    price = Column(Numeric(18, 4), nullable=True)
    batch_no = Column(String(50), nullable=True)
    location = Column(String(100), nullable=True)

    stock_out = relationship("StockOut", back_populates="items")
    goods = relationship("Goods")

