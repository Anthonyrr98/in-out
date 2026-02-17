from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class StockView(QWidget):
    """库存查询占位页面。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("库存查询页面（稍后实现具体功能）", self))

