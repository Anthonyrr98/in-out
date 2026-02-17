from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.user import User
from .base import get_session


class AuthService:
    """简单的用户名密码登录与角色校验。"""

    @staticmethod
    def hash_password(raw: str) -> str:
        # MVP 阶段使用极简 hash，后续可改为 bcrypt/argon2
        import hashlib

        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def verify_password(raw: str, hashed: str) -> bool:
        return AuthService.hash_password(raw) == hashed

    @staticmethod
    def get_or_create_default_admin(session: Session) -> User:
        """确保有一个默认管理员 admin/admin。"""
        user = session.scalar(select(User).where(User.username == "admin"))
        if user:
            return user
        user = User(
            username="admin",
            password_hash=AuthService.hash_password("admin"),
            role="admin",
            is_active=True,
        )
        session.add(user)
        session.flush()
        return user

    @staticmethod
    def login(session: Session, username: str, password: str) -> Optional[User]:
        user = session.scalar(select(User).where(User.username == username))
        if not user or not user.is_active:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        return user

