from datetime import datetime, timedelta

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QDateEdit,
)
from PySide6.QtCore import QDate

from services.base import get_session
from services.report_service import ReportService
from config.settings import EXPORT_DIR


class ReportView(QWidget):
    """报表中心：导出库存汇总与出入库明细。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        main_layout = QVBoxLayout(self)

        # 库存汇总导出
        stock_layout = QHBoxLayout()
        stock_layout.addWidget(QLabel("库存汇总表：", self))
        self.export_stock_btn = QPushButton("导出 Excel", self)
        stock_layout.addWidget(self.export_stock_btn)
        stock_layout.addStretch(1)
        main_layout.addLayout(stock_layout)

        # 出入库明细导出（带日期范围）
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("出入库明细：", self))
        range_layout.addWidget(QLabel("开始日期", self))
        self.start_date_edit = QDateEdit(self)
        self.start_date_edit.setCalendarPopup(True)
        range_layout.addWidget(self.start_date_edit)

        range_layout.addWidget(QLabel("结束日期", self))
        self.end_date_edit = QDateEdit(self)
        self.end_date_edit.setCalendarPopup(True)
        range_layout.addWidget(self.end_date_edit)

        self.export_inout_btn = QPushButton("导出 Excel", self)
        range_layout.addWidget(self.export_inout_btn)
        range_layout.addStretch(1)
        main_layout.addLayout(range_layout)

        main_layout.addStretch(1)

        # 默认日期：最近 30 天
        today = QDate.currentDate()
        self.end_date_edit.setDate(today)
        self.start_date_edit.setDate(today.addDays(-30))

        # 事件绑定
        self.export_stock_btn.clicked.connect(self.export_stock_summary)
        self.export_inout_btn.clicked.connect(self.export_inout_detail)

    def _choose_save_path(self, default_name: str) -> str | None:
        default_path = str(EXPORT_DIR / default_name)
        path, _ = QFileDialog.getSaveFileName(
            self,
            "选择保存位置",
            default_path,
            "Excel 文件 (*.xlsx)",
        )
        return path or None

    def export_stock_summary(self) -> None:
        filepath = self._choose_save_path("库存汇总.xlsx")
        if not filepath:
            return
        try:
            with get_session() as session:
                ReportService.export_stock_summary(session, filepath)
        except Exception as exc:
            QMessageBox.warning(self, "导出失败", str(exc))
            return
        QMessageBox.information(self, "导出完成", f"库存汇总已导出到：\n{filepath}")

    def export_inout_detail(self) -> None:
        filepath = self._choose_save_path("出入库明细.xlsx")
        if not filepath:
            return
        start = self.start_date_edit.date().toPython()
        end = self.end_date_edit.date().toPython() + timedelta(days=1)
        try:
            with get_session() as session:
                ReportService.export_inout_detail(session, filepath, start, end)
        except Exception as exc:
            QMessageBox.warning(self, "导出失败", str(exc))
            return
        QMessageBox.information(self, "导出完成", f"出入库明细已导出到：\n{filepath}")

