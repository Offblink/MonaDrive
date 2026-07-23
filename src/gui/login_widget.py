"""Login panel -- GitHub OAuth entry + credential configuration."""

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.auth import get_github_config, set_github_config
from src.auth.oauth_server import OAuthServer
from src.auth.token_store import delete_token
from src.gui.i18n import t as _t
from src.gui.i18n_mixin import I18nMixin


class _OAuthThread(QThread):
    finished = pyqtSignal(bool, str)

    def run(self):
        server = OAuthServer()
        try:
            token = server.start()
            self.finished.emit(True, token)
        except Exception as e:
            self.finished.emit(False, str(e))
        finally:
            server.stop()


class LoginWidget(QWidget, I18nMixin):
    login_success = pyqtSignal()

    def __init__(self, parent=None):
        # I18nMixin.__init_subclass__ will fire and set up tracking lists
        super().__init__(parent)
        self._oauth_thread: _OAuthThread | None = None
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout()
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.setSpacing(0)
        root.addStretch(3)

        root.addWidget(self._tl("app.title", css="font-size: 28px;"),
                       alignment=Qt.AlignmentFlag.AlignCenter)
        root.addSpacing(8)

        root.addWidget(self._tl("app.tagline", css="font-size: 13px;"),
                       alignment=Qt.AlignmentFlag.AlignCenter)
        root.addSpacing(40)

        card = QWidget()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)
        card_layout.setContentsMargins(24, 24, 24, 24)

        card_layout.addWidget(self._tl("login.client_id", css="font-size: 11px; padding: 0 2px;"))
        self.input_client_id = QLineEdit()
        self.input_client_id.setPlaceholderText("Iv23li...")
        card_layout.addWidget(self.input_client_id)

        card_layout.addWidget(self._tl("login.client_secret", css="font-size: 11px; padding: 0 2px;"))
        self.input_client_secret = QLineEdit()
        self.input_client_secret.setPlaceholderText("...")
        self.input_client_secret.setEchoMode(QLineEdit.EchoMode.Password)
        card_layout.addWidget(self.input_client_secret)

        card.setFixedWidth(440)
        root.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

        root.addSpacing(12)
        self.chk_remember = self._tc("login.remember")
        root.addWidget(self.chk_remember, alignment=Qt.AlignmentFlag.AlignCenter)

        root.addSpacing(16)

        self.btn_login = self._tb("login.signin", "btnPrimary")
        self.btn_login.setFixedHeight(44)
        self.btn_login.setFixedWidth(440)
        self.btn_login.clicked.connect(self._start_oauth)
        root.addWidget(self.btn_login, alignment=Qt.AlignmentFlag.AlignCenter)
        root.addSpacing(16)

        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setMinimumHeight(48)
        self.lbl_status.setStyleSheet("font-size: 12px;")
        root.addWidget(self.lbl_status, alignment=Qt.AlignmentFlag.AlignCenter)
        root.addStretch(3)

        self.setLayout(root)
        self._load_saved()
        self.refresh_text()

    def _load_saved(self):
        cfg = get_github_config()
        if cfg.get("client_id"):
            self.input_client_id.setText(cfg["client_id"])
        if cfg.get("client_secret"):
            self.input_client_secret.setText(cfg["client_secret"])

    def reset(self):
        """Clear inputs and reset button state. Called on logout."""
        self.btn_login.setEnabled(True)
        self._load_saved()
        self.refresh_text()
        self.lbl_status.setText("")

    def _start_oauth(self):
        client_id = self.input_client_id.text().strip()
        client_secret = self.input_client_secret.text().strip()
        if not client_id or not client_secret:
            self.lbl_status.setStyleSheet("color: #f85149; font-size: 12px;")
            self.lbl_status.setText(_t("login.missing_creds"))
            return
        set_github_config(client_id, client_secret)
        self.lbl_status.setStyleSheet("font-size: 12px;")
        self.lbl_status.setText(_t("login.browser_opened"))
        self.btn_login.setEnabled(False)
        self.btn_login.setText(_t("login.waiting"))
        self._oauth_thread = _OAuthThread()
        self._oauth_thread.finished.connect(self._on_oauth_finished)
        self._oauth_thread.start()

    def _on_oauth_finished(self, success: bool, msg: str):
        if success:
            self.lbl_status.setStyleSheet("color: #3fb950; font-size: 12px;")
            self.lbl_status.setText(_t("login.success"))
            self.login_success.emit()
            if not self.chk_remember.isChecked():
                QTimer.singleShot(500, lambda: delete_token())
        else:
            self.btn_login.setEnabled(True)
            self.refresh_text()
            self.lbl_status.setStyleSheet("color: #f85149; font-size: 12px;")
            self.lbl_status.setText(_t("login.failed", msg))
