from datetime import datetime

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
)

from services.base import get_session
from services.stock_out_service import StockOutService, StockOutItemData
from models.stock_out import StockOut
from models.goods import Goods


class StockOutView(QWidget):
    """出库管理页面（列表 + 简单新建对话框）。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("出库单列表", self))
        top.addStretch(1)
        self.new_btn = QPushButton("新建出库单", self)
        top.addWidget(self.new_btn)
        layout.addLayout(top)

        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["单号", "客户", "日期", "类型", "操作员ID"])
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.table, 1)

        self.new_btn.clicked.connect(self.new_stock_out)
        self.refresh_table()

    def refresh_table(self) -> None:
        with get_session() as session:
            rows = session.query(StockOut).order_by(StockOut.date.desc()).limit(200).all()
            self.table.setRowCount(len(rows))
            for i, s in enumerate(rows):
                values = [
                    s.order_no,
                    s.customer or "",
                    s.date.strftime("%Y-%m-%d %H:%M"),
                    s.out_type,
                    "" if s.user_id is None else str(s.user_id),
                ]
                for col, v in enumerate(values):
                    self.table.setItem(i, col, QTableWidgetItem(v))

    def new_stock_out(self) -> None:
        dialog = SimpleStockOutDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                with get_session() as session:
                    StockOutService.create_stock_out(
                        session=session,
                        order_no=data["order_no"],
                        customer=data["customer"],
                        date=datetime.now(),
                        user_id=None,
                        out_type=data["out_type"],
                        items=[
                            StockOutItemData(
                                goods_id=data["goods_id"],
                                quantity=data["quantity"],
                                price=data["price"],
                                batch_no=None,
                                location=None,
                            )
                        ],
                        remark=None,
                    )
            except Exception as exc:
                QMessageBox.warning(self, "错误", str(exc))
            self.refresh_table()


class SimpleStockOutDialog(QDialog):
    """非常简化的出库对话框：一次一个商品。"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("新建出库单")

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.order_no_edit = QLineEdit(self)
        self.customer_edit = QLineEdit(self)
        self.out_type_edit = QLineEdit(self)
        self.goods_code_edit = QLineEdit(self)
        self.quantity_edit = QLineEdit(self)
        self.price_edit = QLineEdit(self)

        form.addRow("出库单号*", self.order_no_edit)
        form.addRow("客户", self.customer_edit)
        form.addRow("类型(sale/use/scrap)", self.out_type_edit)
        form.addRow("商品编码*", self.goods_code_edit)
        form.addRow("数量*", self.quantity_edit)
        form.addRow("单价", self.price_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.out_type_edit.setText("sale")

    def get_data(self) -> dict:
        def _to_float(text: str) -> float:
            return float(text.strip())

        with get_session() as session:
            goods = (
                session.query(Goods)
                .filter(Goods.code == self.goods_code_edit.text().strip())
                .first()
            )
            if not goods:
                raise ValueError("商品编码不存在，请先到商品管理中新增该商品")

        return {
            "order_no": self.order_no_edit.text().strip(),
            "customer": self.customer_edit.text().strip() or None,
            "out_type": self.out_type_edit.text().strip() or "sale",
            "goods_id": goods.id,
            "quantity": _to_float(self.quantity_edit.text()),
            "price": _to_float(self.price_edit.text())
            if self.price_edit.text().strip()
            else None,
        }

