from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
)

from services.base import get_session
from services.auth_service import AuthService


class LoginDialog(QDialog):
    """登录对话框，成功后持有当前用户对象。"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("登录")
        self.current_user = None

        layout = QVBoxLayout(self)
        self.info_label = QLabel("默认管理员账号：admin / admin", self)
        layout.addWidget(self.info_label)

        form = QFormLayout()
        self.username_edit = QLineEdit(self)
        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.Password)
        form.addRow("用户名", self.username_edit)
        form.addRow("密码", self.password_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # 确保默认管理员存在
        with get_session() as session:
            AuthService.get_or_create_default_admin(session)

    def _on_accept(self) -> None:
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        with get_session() as session:
            user = AuthService.login(session, username, password)
            if not user:
                QMessageBox.warning(self, "登录失败", "用户名或密码错误")
                return
            self.current_user = user
        self.accept()

