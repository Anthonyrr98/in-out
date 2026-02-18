from sqlalchemy import Column, Integer, String, Numeric, Text, Boolean

from .base import Base


class Goods(Base):
    """商品表。"""

    __tablename__ = "goods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True, comment="商品编码")
    name = Column(String(200), nullable=False, comment="商品名称")
    category = Column(String(100), nullable=True, comment="分类")
    spec = Column(String(200), nullable=True, comment="规格")
    unit = Column(String(20), nullable=True, comment="单位")
    buy_price = Column(Numeric(18, 4), nullable=True, comment="采购价")
    sell_price = Column(Numeric(18, 4), nullable=True, comment="销售价")
    min_stock = Column(Numeric(18, 4), nullable=True, comment="最低库存预警")
    remark = Column(Text, nullable=True, comment="备注")
    is_active = Column(Boolean, nullable=False, default=True, comment="是否启用")

