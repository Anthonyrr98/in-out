from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class StockInView(QWidget):
    """入库管理占位页面。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("入库管理页面（稍后实现具体功能）", self))

