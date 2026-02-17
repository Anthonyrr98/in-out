from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
)


class GoodsView(QWidget):
    """商品管理界面占位实现。

    后续会注入 GoodsService 并加载真实数据。
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        main_layout = QVBoxLayout(self)

        # 顶部查询区域
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("关键字：", self))
        self.keyword_edit = QLineEdit(self)
        search_layout.addWidget(self.keyword_edit)
        self.search_btn = QPushButton("查询", self)
        search_layout.addWidget(self.search_btn)
        search_layout.addStretch(1)

        main_layout.addLayout(search_layout)

        # 中部表格
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["编码", "名称", "分类", "规格", "单位"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.table, 1)

        # 底部按钮
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("新增", self)
        self.edit_btn = QPushButton("编辑", self)
        self.delete_btn = QPushButton("删除", self)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch(1)

        main_layout.addLayout(btn_layout)

        # 简单填充几行示例数据，证明 UI 可用
        self._load_demo_data()

    def _load_demo_data(self) -> None:
        demo_rows = [
            ("SP001", "示例商品A", "分类1", "规格1", "件"),
            ("SP002", "示例商品B", "分类2", "规格2", "箱"),
        ]
        self.table.setRowCount(len(demo_rows))
        for row, data in enumerate(demo_rows):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

