import sys

from PySide6.QtWidgets import QApplication

from models.base import init_db
from ui.main_window import MainWindow


def main() -> None:
    """应用入口。"""
    # 初始化数据库
    init_db()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

