"""Main window -- theme toggle, language toggle, login/dashboard switching. v3"""

import sys

from pathlib import Path

from PyQt6.QtCore import QEasingCurve, QEvent, QPropertyAnimation, Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtNetwork import QLocalServer
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QStackedWidget,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from src.auth.token_store import get_token
from src.gui.dashboard_widget import DashboardWidget
from src.gui.i18n import get_language, set_language
from src.gui.login_widget import LoginWidget
from src.gui.themes import get_theme, DARK


class MainWindow(QMainWindow):
    WINDOW_TITLE = "MonaDrive"
    WIDTH_L = 580
    HEIGHT_L = 600
    WIDTH_D = 780
    HEIGHT_D = 700

    def __init__(self):
        super().__init__()
        self._dark = True
        self._lang = get_language()
        self.setWindowTitle(self.WINDOW_TITLE)
        icon = Path(__file__).parent.parent.parent / "mona.ico"
        if icon.is_file(): self.setWindowIcon(QIcon(str(icon)))
        self.setMinimumSize(self.WIDTH_L, self.HEIGHT_L)
        self.resize(self.WIDTH_L, self.HEIGHT_L)
        self.setStyleSheet(DARK)
        self._ensure_git()

        self._central = QWidget()
        self.setCentralWidget(self._central)
        self._root_layout = QVBoxLayout(self._central)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(12, 8, 12, 0)
        top_bar.addStretch()

        self._btn_help = QPushButton("?")
        self._btn_help.setObjectName("btnIcon")
        self._btn_help.clicked.connect(self._show_help)
        top_bar.addWidget(self._btn_help)

        self._btn_lang = QPushButton(self._lang_label())
        self._btn_lang.setObjectName("btnIcon")
        self._btn_lang.clicked.connect(self._toggle_language)
        top_bar.addWidget(self._btn_lang)

        self._btn_theme = QPushButton(self._theme_label())
        self._btn_theme.setObjectName("btnIcon")
        self._btn_theme.clicked.connect(self._toggle_theme)
        top_bar.addWidget(self._btn_theme)

        self._refresh_tooltips()

        self._root_layout.addLayout(top_bar)

        self._stack = QStackedWidget()
        self._root_layout.addWidget(self._stack, 1)

        self._login_widget = LoginWidget()
        self._dashboard = DashboardWidget()
        self._stack.addWidget(self._login_widget)
        self._stack.addWidget(self._dashboard)

        self._login_widget.login_success.connect(self._on_login_success)
        self._dashboard.logout.connect(self._on_logout)

        if get_token():
            self._on_login_success()

        # --- 系统托盘 ---
        self._create_tray_icon()

        # --- 单实例 IPC：重复启动时唤醒已有窗口 ---
        self._ipc_server = QLocalServer(self)
        self._ipc_server.listen("MonaDriveIPC")
        self._ipc_server.newConnection.connect(self._restore_from_tray)

    def _ensure_git(self):
        """Check for git on startup; download Portable Git if missing."""
        from src.git_setup import get_git, download_git

        if get_git():
            return

        reply = QMessageBox.question(
            None, "MonaDrive",
            "需要 Git 才能运行，是否自动下载？(~50 MB)\n\n"
            "Git is required. Download now? (~50 MB)",
        )
        if reply != QMessageBox.StandardButton.Yes:
            sys.exit(0)

        progress = QProgressDialog("正在下载 Git...", "取消", 0, 0, None)
        progress.setWindowTitle("MonaDrive")
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.setCancelButton(None)
        progress.show()
        QApplication.processEvents()

        def on_progress(done: int, total: int):
            if total > 0:
                progress.setMaximum(total)
                progress.setValue(done)
                progress.setLabelText(
                    f"下载 Git 中... {done // 1024 // 1024} / {total // 1024 // 1024} MB"
                )
            QApplication.processEvents()

        try:
            download_git(on_progress)
        except Exception as e:
            progress.close()
            QMessageBox.critical(None, "错误", f"Git 下载失败:\n{e}")
            sys.exit(1)

        progress.close()

    # ---- theme ----

    def _theme_label(self) -> str:
        return "\u263d" if self._dark else "\u2600"

    def _toggle_theme(self):
        self._dark = not self._dark
        self._btn_theme.setText(self._theme_label())

        effect = QGraphicsOpacityEffect(self._stack)
        self._stack.setGraphicsEffect(effect)

        self._anim_out = QPropertyAnimation(effect, b"opacity")
        self._anim_out.setDuration(300)
        self._anim_out.setStartValue(1.0)
        self._anim_out.setEndValue(0.0)
        self._anim_out.setEasingCurve(QEasingCurve.Type.InCubic)

        def _apply_and_fade_in():
            self.setStyleSheet(get_theme(self._dark))
            self._login_widget.refresh_text()
            self._dashboard.refresh_text()
            self._anim_in = QPropertyAnimation(effect, b"opacity")
            self._anim_in.setDuration(300)
            self._anim_in.setStartValue(0.0)
            self._anim_in.setEndValue(1.0)
            self._anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._anim_in.finished.connect(lambda: self._stack.setGraphicsEffect(None))
            self._anim_in.start()

        self._anim_out.finished.connect(_apply_and_fade_in)
        self._anim_out.start()

    # ---- language ----

    def _lang_label(self) -> str:
        return "\u4e2d" if self._lang == "zh" else "E"

    def _toggle_language(self):
        self._lang = "en" if self._lang == "zh" else "zh"
        set_language(self._lang)
        self._btn_lang.setText(self._lang_label())

        effect = QGraphicsOpacityEffect(self._stack)
        self._stack.setGraphicsEffect(effect)

        self._lang_anim_out = QPropertyAnimation(effect, b"opacity")
        self._lang_anim_out.setDuration(200)
        self._lang_anim_out.setStartValue(1.0)
        self._lang_anim_out.setEndValue(0.0)
        self._lang_anim_out.setEasingCurve(QEasingCurve.Type.InCubic)

        def _apply_and_fade_in():
            self._login_widget.refresh_text()
            self._dashboard.refresh_text()
            self._refresh_tooltips()
            self._lang_anim_in = QPropertyAnimation(effect, b"opacity")
            self._lang_anim_in.setDuration(200)
            self._lang_anim_in.setStartValue(0.0)
            self._lang_anim_in.setEndValue(1.0)
            self._lang_anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._lang_anim_in.finished.connect(lambda: self._stack.setGraphicsEffect(None))
            self._lang_anim_in.start()

        self._lang_anim_out.finished.connect(_apply_and_fade_in)
        self._lang_anim_out.start()

    # ---- navigation ----

    def _on_login_success(self):
        self._stack.setCurrentWidget(self._dashboard)
        self.resize(self.WIDTH_D, self.HEIGHT_D)
        self._dashboard.reload()

    def _on_logout(self):
        self._stack.setCurrentWidget(self._login_widget)
        self.resize(self.WIDTH_L, self.HEIGHT_L)
        self._login_widget.reset()

    def _show_help(self):
        from PyQt6.QtWidgets import QMessageBox
        from src.gui.i18n import t as _t
        QMessageBox.information(self, _t("help.title"), _t("help.body"))

    def _refresh_tooltips(self):
        from src.gui.i18n import t as _t
        self._btn_help.setToolTip(_t("tooltip.help"))
        self._btn_lang.setToolTip(_t("tooltip.language"))
        self._btn_theme.setToolTip(_t("tooltip.theme"))

    # ========================
    # System Tray
    # ========================

    def _create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = Path(__file__).parent.parent.parent / "mona.ico"
        if icon_path.is_file():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        else:
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))

        menu = QMenu()
        show_action = QAction("打开主界面", self)
        show_action.triggered.connect(self._restore_from_tray)
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self._quit_application)
        menu.addAction(show_action)
        menu.addAction(quit_action)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._restore_from_tray()

    def _minimize_to_tray(self):
        self.hide()

    def _restore_from_tray(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def _quit_application(self):
        if self.tray_icon:
            self.tray_icon.hide()
        QApplication.quit()


    def changeEvent(self, event):
        if event.type() == QEvent.Type.ActivationChange and self.isActiveWindow():
            self._dashboard.on_window_activated()
        super().changeEvent(event)
    def closeEvent(self, event):
        event.ignore()
        self._minimize_to_tray()
