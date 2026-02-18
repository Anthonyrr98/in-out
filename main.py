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

    # 全局手绘 + Claymorphism 风格样式
    app.setStyleSheet(
        """
QMainWindow {
    background: #FAFAF8;
    font-family: "Segoe UI";
}

QDialog {
    background: #FAFAF8;
    font-family: "Segoe UI";
}

/* 左侧菜单：纸片卡片 + 粗描边 */
QListWidget {
    background: #FAF5FF;
    border: 3px solid #4A4A4A;
    border-radius: 18px;
    padding: 8px;
}
QListWidget::item {
    padding: 8px 6px;
}
QListWidget::item:selected {
    background: #C4A77D;
    color: #1A1A1A;
    border-radius: 12px;
}

/* 通用按钮：圆角+粗描边+主色填充 */
QPushButton {
    background: #7C3AED;
    color: white;
    border-radius: 16px;
    border: 3px solid #4A4A4A;
    padding: 6px 14px;
}
QPushButton:hover {
    background: #A78BFA;
}
QPushButton:disabled {
    background: #E5E7EB;
    color: #9CA3AF;
    border-color: #9CA3AF;
}

/* 输入框：轻描边，圆角 */
QLineEdit, QDateEdit, QComboBox {
    background: #FFFFFF;
    border-radius: 10px;
    border: 2px solid #C4A77D;
    padding: 4px 8px;
}

/* 表格：浅纸色背景 + 手绘网格线 */
QTableWidget {
    background: #FAFAF8;
    gridline-color: #C4A77D;
}
QHeaderView::section {
    background: #EDE9FE;
    border: 0px;
    border-bottom: 3px solid #4A4A4A;
    padding: 4px 6px;
    font-weight: 600;
}
QTableWidget::item:selected {
    background: #FDE68A;
    color: #1A1A1A;
}

QStatusBar {
    background: #EDE9FE;
}
"""
    )

    login = LoginDialog()
    if login.exec() != LoginDialog.Accepted:
        return

    window = MainWindow(current_user=login.current_user)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

