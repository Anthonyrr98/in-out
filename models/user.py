from sqlalchemy import Column, Integer, String, Boolean

from .base import Base


class User(Base):
    """用户与角色表。"""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="operator")  # admin / operator / viewer
    is_active = Column(Boolean, nullable=False, default=True)

