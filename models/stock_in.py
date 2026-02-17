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


class StockIn(Base):
    """入库单主表。"""

    __tablename__ = "stock_in"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(50), nullable=False, unique=True, index=True, comment="入库单号")
    supplier = Column(String(200), nullable=True, comment="供应商")
    date = Column(DateTime, nullable=False, default=datetime.now, comment="入库日期")
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True, comment="操作员用户ID")
    remark = Column(Text, nullable=True)

    user = relationship("User", backref="stock_in_orders")
    items = relationship("StockInItem", back_populates="stock_in", cascade="all, delete-orphan")


class StockInItem(Base):
    """入库单明细表。"""

    __tablename__ = "stock_in_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_in_id = Column(Integer, ForeignKey("stock_in.id"), nullable=False, index=True)
    goods_id = Column(Integer, ForeignKey("goods.id"), nullable=False, index=True)
    quantity = Column(Numeric(18, 4), nullable=False)
    price = Column(Numeric(18, 4), nullable=True)
    batch_no = Column(String(50), nullable=True)
    location = Column(String(100), nullable=True)

    stock_in = relationship("StockIn", back_populates="items")
    goods = relationship("Goods")

