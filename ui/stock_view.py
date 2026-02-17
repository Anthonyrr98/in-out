from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem

from services.stock_service import StockService
from services.base import get_session


class StockView(QWidget):
    """库存查询页面。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # 顶部查询
        top = QHBoxLayout()
        top.addWidget(QLabel("关键字：", self))
        self.keyword_edit = QLineEdit(self)
        top.addWidget(self.keyword_edit)
        self.search_btn = QPushButton("查询", self)
        top.addWidget(self.search_btn)
        top.addStretch(1)
        layout.addLayout(top)

        # 表格
        self.table = QTableWidget(self)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["编码", "名称", "分类", "库存数量", "批次", "库位", "有效期"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, 1)

        self.search_btn.clicked.connect(self.refresh_table)
        self.refresh_table()

    def refresh_table(self) -> None:
        from models.stock import Stock  # 避免循环导入

        keyword = self.keyword_edit.text().strip() or None
        with get_session() as session:
            rows, _ = StockService.list_stock(
                session, keyword=keyword, only_warning=False, page=1, page_size=500
            )
            self.table.setRowCount(len(rows))
            for row, s in enumerate(rows):
                goods = s.goods
                values = [
                    goods.code if goods else "",
                    goods.name if goods else "",
                    goods.category if goods else "",
                    str(s.quantity),
                    s.batch_no or "",
                    s.location or "",
                    "" if not s.expire_date else s.expire_date.strftime("%Y-%m-%d"),
                ]
                for col, v in enumerate(values):
                    item = QTableWidgetItem(v)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, item)


