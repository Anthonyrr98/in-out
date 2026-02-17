import sys

from PySide6.QtWidgets import QApplication

from models.base import init_db
from ui.main_window import MainWindow
from ui.login_dialog import LoginDialog


def main() -> None:
    """应用入口。"""
    # 初始化数据库
    init_db()

    app = QApplication(sys.argv)

    login = LoginDialog()
    if login.exec() != LoginDialog.Accepted:
        return

    window = MainWindow(current_user=login.current_user)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

