from datetime import datetime

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QMessageBox,
    QHeaderView,
    QDateEdit,
)

from services.base import get_session
from services.stock_in_service import StockInService, StockInItemData
from models.stock_in import StockIn
from models.goods import Goods


class StockInView(QWidget):
    """入库管理页面（列表 + 简单新建对话框）。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("入库单列表", self))
        top.addStretch(1)
        top.addWidget(QLabel("开始日期", self))
        self.start_date = QDateEdit(self)
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        top.addWidget(self.start_date)
        top.addWidget(QLabel("结束日期", self))
        self.end_date = QDateEdit(self)
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        top.addWidget(self.end_date)
        self.filter_btn = QPushButton("筛选", self)
        top.addWidget(self.filter_btn)
        self.new_btn = QPushButton("新建入库单", self)
        top.addWidget(self.new_btn)
        layout.addLayout(top)

        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["单号", "供应商", "日期", "操作员ID"])
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.table, 1)

        self.filter_btn.clicked.connect(self.refresh_table)
        self.new_btn.clicked.connect(self.new_stock_in)
        self.refresh_table()

    def refresh_table(self) -> None:
        start_dt = self.start_date.date().toPython()
        end_dt = self.end_date.date().toPython()
        with get_session() as session:
            q = session.query(StockIn).order_by(StockIn.date.desc())
            q = q.filter(StockIn.date.between(start_dt, datetime(end_dt.year, end_dt.month, end_dt.day, 23, 59, 59)))
            rows = q.limit(200).all()
            self.table.setRowCount(len(rows))
            for i, s in enumerate(rows):
                values = [
                    s.order_no,
                    s.supplier or "",
                    s.date.strftime("%Y-%m-%d %H:%M"),
                    "" if s.user_id is None else str(s.user_id),
                ]
                for col, v in enumerate(values):
                    self.table.setItem(i, col, QTableWidgetItem(v))

    def new_stock_in(self) -> None:
        dialog = SimpleStockInDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                with get_session() as session:
                    StockInService.create_stock_in(
                        session=session,
                        order_no=data["order_no"],
                        supplier=data["supplier"],
                        date=datetime.now(),
                        user_id=None,
                        items=[
                            StockInItemData(
                                goods_id=item["goods_id"],
                                quantity=item["quantity"],
                                price=item.get("price"),
                                batch_no=None,
                                location=None,
                            )
                            for item in data["items"]
                        ],
                        remark=None,
                    )
            except Exception as exc:
                QMessageBox.warning(self, "错误", str(exc))
            self.refresh_table()


class SimpleStockInDialog(QDialog):
    """非常简化的入库对话框：支持多行明细。"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("新建入库单")

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.order_no_edit = QLineEdit(self)
        self.supplier_edit = QLineEdit(self)

        form.addRow("入库单号*", self.order_no_edit)
        form.addRow("供应商", self.supplier_edit)

        layout.addLayout(form)

        # 明细表格
        self.items_table = QTableWidget(self)
        self.items_table.setColumnCount(3)
        self.items_table.setHorizontalHeaderLabels(["商品编码*", "数量*", "单价"])
        header = self.items_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.items_table)

        # 明细操作按钮
        btn_row = QHBoxLayout()
        self.add_row_btn = QPushButton("添加明细行", self)
        self.remove_row_btn = QPushButton("删除选中行", self)
        btn_row.addWidget(self.add_row_btn)
        btn_row.addWidget(self.remove_row_btn)
        btn_row.addStretch(1)
        layout.addLayout(btn_row)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.add_row_btn.clicked.connect(self._add_row)
        self.remove_row_btn.clicked.connect(self._remove_row)
        self._add_row()

    def _add_row(self) -> None:
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)

    def _remove_row(self) -> None:
        row = self.items_table.currentRow()
        if row >= 0:
            self.items_table.removeRow(row)

    def _on_accept(self) -> None:
        if not self.order_no_edit.text().strip():
            QMessageBox.warning(self, "校验失败", "入库单号为必填项")
            return
        if self.items_table.rowCount() == 0:
            QMessageBox.warning(self, "校验失败", "至少需要一行入库明细")
            return
        # 尝试解析数据以提前发现错误
        try:
            _ = self._collect_items()
        except Exception as exc:
            QMessageBox.warning(self, "校验失败", str(exc))
            return
        self.accept()

    def _collect_items(self) -> list[dict]:
        def _to_float(text: str) -> float:
            return float(text.strip())

        items: list[dict] = []
        with get_session() as session:
            for row in range(self.items_table.rowCount()):
                code_item = self.items_table.item(row, 0)
                qty_item = self.items_table.item(row, 1)
                price_item = self.items_table.item(row, 2)
                code = (code_item.text().strip() if code_item else "") if code_item else ""
                qty_text = qty_item.text().strip() if qty_item else ""
                if not code or not qty_text:
                    raise ValueError("商品编码和数量为必填项")
                goods = (
                    session.query(Goods)
                    .filter(Goods.code == code)
                    .first()
                )
                if not goods:
                    raise ValueError(f"商品编码不存在: {code}")
                quantity = _to_float(qty_text)
                if quantity <= 0:
                    raise ValueError("数量必须大于 0")
                price = None
                if price_item and price_item.text().strip():
                    price = _to_float(price_item.text())
                items.append(
                    {
                        "goods_id": goods.id,
                        "quantity": quantity,
                        "price": price,
                    }
                )
        return items

    def get_data(self) -> dict:
        items = self._collect_items()
        return {
            "order_no": self.order_no_edit.text().strip(),
            "supplier": self.supplier_edit.text().strip() or None,
            "items": items,
        }


