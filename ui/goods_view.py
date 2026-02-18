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
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QMessageBox,
    QHeaderView,
)

from services.goods_service import GoodsService
from services.base import get_session
from models.goods import Goods

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
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
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

        # 事件连接
        self.search_btn.clicked.connect(self.refresh_table)
        self.add_btn.clicked.connect(self.add_goods)
        self.edit_btn.clicked.connect(self.edit_goods)
        self.delete_btn.clicked.connect(self.delete_goods)
        self.table.cellDoubleClicked.connect(lambda _r, _c: self.edit_goods())

        # 初次加载
        self.refresh_table()

    # ---------- 数据加载 ----------
    def refresh_table(self) -> None:
        keyword = self.keyword_edit.text().strip() or None
        with get_session() as session:
            service = GoodsService(session)
            rows, _ = service.list(session, keyword=keyword, page=1, page_size=200)
            self._fill_table(rows)

    def _fill_table(self, goods_list: list[Goods]) -> None:
        self.table.setRowCount(len(goods_list))
        for row, g in enumerate(goods_list):
            values = [g.code, g.name, g.category or "", g.spec or "", g.unit or ""]
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setData(Qt.UserRole, g.id)
                if col == 0:
                    # 只在第一列存 id
                    item.setData(Qt.UserRole, g.id)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def _get_selected_goods_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if not item:
            return None
        gid = item.data(Qt.UserRole)
        return int(gid) if gid is not None else None

    # ---------- 按钮操作 ----------
    def add_goods(self) -> None:
        dialog = GoodsEditDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                with get_session() as session:
                    GoodsService.create(session, **data)
            except Exception as exc:
                QMessageBox.warning(self, "错误", str(exc))
            self.refresh_table()

    def edit_goods(self) -> None:
        gid = self._get_selected_goods_id()
        if gid is None:
            QMessageBox.information(self, "提示", "请先选择一条商品记录")
            return
        with get_session() as session:
            goods = session.get(Goods, gid)
            if not goods:
                QMessageBox.warning(self, "错误", "商品不存在，可能已被删除")
                return
            dialog = GoodsEditDialog(self, goods)
            if dialog.exec() == QDialog.Accepted:
                data = dialog.get_data()
                try:
                    GoodsService.update(session, gid, **data)
                except Exception as exc:
                    QMessageBox.warning(self, "错误", str(exc))
        self.refresh_table()

    def delete_goods(self) -> None:
        gid = self._get_selected_goods_id()
        if gid is None:
            QMessageBox.information(self, "提示", "请先选择一条商品记录")
            return
        if (
            QMessageBox.question(self, "确认删除", "确定要删除选中的商品吗？")
            != QMessageBox.Yes
        ):
            return
        with get_session() as session:
            GoodsService.delete(session, gid)
        self.refresh_table()


class GoodsEditDialog(QDialog):
    """新增/编辑商品对话框。"""

    def __init__(self, parent: QWidget | None = None, goods: Goods | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("编辑商品" if goods else "新增商品")
        self._goods = goods

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.code_edit = QLineEdit(self)
        self.name_edit = QLineEdit(self)
        self.category_edit = QLineEdit(self)
        self.spec_edit = QLineEdit(self)
        self.unit_edit = QLineEdit(self)
        self.buy_price_edit = QLineEdit(self)
        self.sell_price_edit = QLineEdit(self)
        self.min_stock_edit = QLineEdit(self)
        self.remark_edit = QLineEdit(self)

        form.addRow("编码*", self.code_edit)
        form.addRow("名称*", self.name_edit)
        form.addRow("分类", self.category_edit)
        form.addRow("规格", self.spec_edit)
        form.addRow("单位", self.unit_edit)
        form.addRow("采购价", self.buy_price_edit)
        form.addRow("销售价", self.sell_price_edit)
        form.addRow("最低库存", self.min_stock_edit)
        form.addRow("备注", self.remark_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if goods:
            self._load_goods(goods)

    def _load_goods(self, g: Goods) -> None:
        self.code_edit.setText(g.code)
        self.name_edit.setText(g.name)
        self.category_edit.setText(g.category or "")
        self.spec_edit.setText(g.spec or "")
        self.unit_edit.setText(g.unit or "")
        self.buy_price_edit.setText("" if g.buy_price is None else str(g.buy_price))
        self.sell_price_edit.setText("" if g.sell_price is None else str(g.sell_price))
        self.min_stock_edit.setText("" if g.min_stock is None else str(g.min_stock))
        self.remark_edit.setText(g.remark or "")

    def _on_accept(self) -> None:
        if not self.code_edit.text().strip() or not self.name_edit.text().strip():
            QMessageBox.warning(self, "校验失败", "编码和名称为必填项")
            return
        self.accept()

    def get_data(self) -> dict:
        def _to_float(text: str) -> float | None:
            t = text.strip()
            if not t:
                return None
            try:
                return float(t)
            except ValueError:
                return None

        return {
            "code": self.code_edit.text().strip(),
            "name": self.name_edit.text().strip(),
            "category": self.category_edit.text().strip() or None,
            "spec": self.spec_edit.text().strip() or None,
            "unit": self.unit_edit.text().strip() or None,
            "buy_price": _to_float(self.buy_price_edit.text()),
            "sell_price": _to_float(self.sell_price_edit.text()),
            "min_stock": _to_float(self.min_stock_edit.text()),
            "remark": self.remark_edit.text().strip() or None,
        }


