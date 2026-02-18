from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from config.settings import DB_FILE, DATA_DIR
# SQLAlchemy 基础 Base 类
Base = declarative_base()


def get_db_path():
    """返回 SQLite 数据库文件路径（集中由 config.settings 管理）。"""
    return DB_FILE


_ENGINE = create_engine(
    f"sqlite:///{get_db_path()}",
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(bind=_ENGINE, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)


def get_engine():
    """对外暴露 engine，方便 Alembic 或其他工具使用。"""
    return _ENGINE


def init_db() -> None:
    """创建所有表结构。应在应用启动时调用一次。"""
    import models.goods  # noqa: F401
    import models.stock  # noqa: F401
    import models.stock_in  # noqa: F401
    import models.stock_out  # noqa: F401
    import models.user  # noqa: F401
    import models.stock_flow  # noqa: F401

    Base.metadata.create_all(bind=_ENGINE)

