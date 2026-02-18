from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QListWidget,
    QStackedWidget,
    QListWidgetItem,
    QLabel,
)

from ui.goods_view import GoodsView
from ui.stock_in_view import StockInView
from ui.stock_out_view import StockOutView
from ui.stock_view import StockView
from ui.report_view import ReportView


class MainWindow(QMainWindow):
    """应用主窗口：左侧菜单 + 右侧内容区。"""

    def __init__(self, current_user=None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.current_user = current_user
        self.setWindowTitle("库存管理系统")
        self.resize(1100, 700)

        central = QWidget(self)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        # 左侧菜单
        self.menu_list = QListWidget(central)
        self.menu_list.setFixedWidth(180)
        self.menu_list.addItem(QListWidgetItem("商品管理"))          # index 0
        self.menu_list.addItem(QListWidgetItem("入库管理"))          # index 1
        self.menu_list.addItem(QListWidgetItem("出库管理"))          # index 2
        self.menu_list.addItem(QListWidgetItem("库存查询"))          # index 3
        # 报表中心仅管理员和只读用户可见
        self.report_index = None
        role = getattr(self.current_user, "role", "admin")
        if role in ("admin", "viewer"):
            self.report_index = self.menu_list.count()
            self.menu_list.addItem(QListWidgetItem("报表中心"))      # index 4 (if added)

        # 右侧内容区
        self.stack = QStackedWidget(central)
        self.goods_view = GoodsView()
        self.stock_in_view = StockInView()
        self.stock_out_view = StockOutView()
        self.stock_view = StockView()
        self.report_view = ReportView()

        self.stack.addWidget(self.goods_view)
        self.stack.addWidget(self.stock_in_view)
        self.stack.addWidget(self.stock_out_view)
        self.stack.addWidget(self.stock_view)
        self.stack.addWidget(self.report_view)

        layout.addWidget(self.menu_list)
        layout.addWidget(self.stack, 1)

        self.setCentralWidget(central)

        self.menu_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.menu_list.setCurrentRow(0)

        role = getattr(self.current_user, "role", None)

        # 简单基于角色的按钮控制示例
        if role == "viewer":
            self.goods_view.add_btn.setEnabled(False)
            self.goods_view.edit_btn.setEnabled(False)
            self.goods_view.delete_btn.setEnabled(False)
            self.stock_in_view.new_btn.setEnabled(False)
            self.stock_out_view.new_btn.setEnabled(False)

        # 状态栏显示当前用户信息
        user_name = getattr(self.current_user, "username", "未知用户")
        role = role or "unknown"
        status = self.statusBar()
        status.showMessage(f"当前用户：{user_name}（角色：{role}）")

