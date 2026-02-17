from contextlib import contextmanager
from typing import Iterator

from sqlalchemy.orm import Session

from models.base import SessionLocal


@contextmanager
def get_session() -> Iterator[Session]:
    """获取一个自动提交/回滚的会话上下文。"""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

