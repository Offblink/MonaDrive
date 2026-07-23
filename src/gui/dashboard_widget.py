"""Dashboard -- setup wizard, sync panel with file sidebar. Unified i18n via I18nMixin.

Layout: QSplitter for resizable sections (sync | log | files).
File sidebar supports directory navigation with back button.
"""

import json, os, shutil
from pathlib import Path

from PyQt6.QtCore import QSize, Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QCursor
from PyQt6.QtGui import QMovie, QPixmap, QPainter, QPainterPath
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QDialog, QDialogButtonBox, QFileDialog,
    QHBoxLayout, QInputDialog, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMenu, QMessageBox, QPlainTextEdit, QPushButton,
    QSplitter, QStackedWidget, QVBoxLayout, QWidget, QSizePolicy,
)

from src.auth import CONFIG_DIR, CONFIG_FILE
from src.auth.token_store import delete_token, get_token
from src.github_api.client import GitHubClient
from src.sync.engine import SyncEngine

from src.gui.i18n import t as _t
from src.gui.i18n_mixin import I18nMixin


class _SyncThread(QThread):
    finished = pyqtSignal(bool, str)
    def __init__(self, engine: SyncEngine, action: str, exclude: list[str] | None = None):
        super().__init__(); self.engine, self.action, self.exclude = engine, action, exclude
        self.cancelled = False
    def run(self):
        try:
            if self.cancelled: return
            if self.action == "push":
                r = self.engine.commit_and_push(exclude=self.exclude)
                if self.cancelled: return
                self.finished.emit(True, _t("dash.push_result", r) if r else _t("dash.nothing_push"))
            else:
                r = self.engine.pull()
                if self.cancelled: return
                s = (r or "").strip().lower()
                if not s or "up to date" in s: self.finished.emit(True, _t("dash.uptodate"))
                else: self.finished.emit(True, _t("dash.pull_result", s))
        except Exception as e:
            if not self.cancelled: self.finished.emit(False, str(e))

class _SetupThread(QThread):
    finished = pyqtSignal(bool, str)
    def __init__(self, repo_name: str, local_path: str, config: dict, config_path: Path):
        super().__init__(); self.repo_name, self.local_path = repo_name, local_path
        self.config, self.config_path = config, config_path
    def run(self):
        try:
            c = GitHubClient(); r = c.get_or_create_repo(self.repo_name, private=True)
            e = SyncEngine(self.local_path, r["full_name"]); e.clone()
            self.config.update(repo_name=self.repo_name, local_path=self.local_path, repo_full_name=r["full_name"])
            self.config_path.write_text(json.dumps(self.config, indent=2, ensure_ascii=False), encoding="utf-8")
            self.finished.emit(True, "")
        except Exception as ex: self.finished.emit(False, str(ex))


class _LoadReposThread(QThread):
    finished = pyqtSignal(bool, list, str)  # ok, repos, error
    def run(self):
        try:
            c = GitHubClient(); repos = c.list_repos()
            self.finished.emit(True, repos, "")
        except Exception as e: self.finished.emit(False, [], str(e))


class _RepoActionThread(QThread):
    finished = pyqtSignal(bool, str)
    def __init__(self, action: str, name: str, new_name: str = "", private: bool = True):
        super().__init__(); self.action, self.name, self.new_name = action, name, new_name
        self.private = private
    def run(self):
        try:
            c = GitHubClient()
            if self.action == "create": c.create_repo(self.name, self.private)
            elif self.action == "rename": c.rename_repo(self.name, self.new_name)
            elif self.action == "delete": c.delete_repo(self.name)
            self.finished.emit(True, "")
        except Exception as e: self.finished.emit(False, str(e))




class _RepoItemWidget(QWidget):
    """Repo list item with hover-to-show rename/delete buttons."""
    def __init__(self, repo: dict, on_rename, on_delete, parent=None):
        super().__init__(parent); self._repo = repo
        row = QHBoxLayout(); row.setContentsMargins(8, 3, 8, 3); row.setSpacing(4)
        self.lbl = QLabel(repo["name"]); self.lbl.setStyleSheet("font-size:11px;background:transparent;")
        self.lbl.setWordWrap(False); self.lbl.setMinimumWidth(80)
        row.addWidget(self.lbl, 1)
        self.br = QPushButton("\u270f"); self.br.setFixedSize(22, 22)
        self.br.setStyleSheet("QPushButton{background:transparent;border:none;font-size:13px;padding:0} QPushButton:hover{background:rgba(128,128,128,0.25);border-radius:3px}")
        self.br.hide(); self.br.clicked.connect(lambda: on_rename(repo["name"])); row.addWidget(self.br)
        self.bd = QPushButton("\U0001f5d1"); self.bd.setFixedSize(22, 22)
        self.bd.setStyleSheet("QPushButton{background:transparent;border:none;font-size:13px;padding:0} QPushButton:hover{background:rgba(220,60,60,0.3);border-radius:3px}")
        self.bd.hide(); self.bd.clicked.connect(lambda: on_delete(repo["name"])); row.addWidget(self.bd)
        self.setLayout(row); self.setStyleSheet("background:transparent;")
    def enterEvent(self, e): self.br.show(); self.bd.show(); super().enterEvent(e)
    def leaveEvent(self, e): self.br.hide(); self.bd.hide(); super().leaveEvent(e)
class _SetupPage(QWidget, I18nMixin):
    setup_done = pyqtSignal()
    def __init__(self, config: dict, config_path: Path, parent=None):
        super().__init__(parent); self._config, self._config_path = config, config_path
        self._setup_thread: _SetupThread | None = None; self._repos: list[dict] = []
        self._selected_repo: dict | None = None
        self._setup_ui(); self._load_repos()
    def _setup_ui(self):
        h = QHBoxLayout(self); h.setContentsMargins(0,0,0,0); h.setSpacing(0)
        # --- sidebar ---
        sidebar = QWidget(); sidebar.setObjectName("repoSidebar"); sidebar.setFixedWidth(240)
        sv = QVBoxLayout(sidebar); sv.setContentsMargins(12,12,12,12); sv.setSpacing(6)
        sv.addWidget(self._tl("dash.repos", css="font-size:13px;padding:0 4px 4px 4px;"))
        row = QHBoxLayout(); row.setSpacing(4)
        self.btn_new_repo = self._tb("dash.new_repo"); self.btn_new_repo.clicked.connect(self._do_new_repo); row.addWidget(self.btn_new_repo)
        self.btn_refresh_repos = QPushButton("\u21bb"); self.btn_refresh_repos.setObjectName("btnNavIcon"); self.btn_refresh_repos.setFixedSize(28, 28)
        self.btn_refresh_repos.clicked.connect(self._load_repos); row.addWidget(self.btn_refresh_repos)
        row.addStretch(); sv.addLayout(row)
        self.repo_list = QListWidget()
        self.repo_list.setStyleSheet("QListWidget::item { padding: 0px; }")
        self.repo_list.itemClicked.connect(self._on_repo_selected)
        sv.addWidget(self.repo_list, 1)
        h.addWidget(sidebar)
        # --- main ---
        main = QWidget(); mv = QVBoxLayout(main); mv.setAlignment(Qt.AlignmentFlag.AlignCenter); mv.setContentsMargins(32,16,32,16)
        mv.addWidget(self._tl("dash.setup_title", css="font-size:20px;padding-bottom:8px;"), alignment=Qt.AlignmentFlag.AlignCenter)
        mv.addWidget(self._tl("dash.repo_name", css="font-size:11px;padding:0 2px;"))
        self.input_repo = QLineEdit(); self.input_repo.setPlaceholderText(_t("dash.repo_placeholder")); self.input_repo.setMinimumWidth(320); self.input_repo.setReadOnly(True)
        mv.addWidget(self.input_repo); mv.addSpacing(12)
        mv.addWidget(self._tl("dash.folder", css="font-size:11px;padding:0 2px;"))
        row = QHBoxLayout(); self.input_path = QLineEdit(); self.input_path.setPlaceholderText(_t("dash.folder_placeholder"))
        row.addWidget(self.input_path, 1)
        b = self._tb("dash.browse"); b.clicked.connect(self._browse); row.addWidget(b); mv.addLayout(row)
        mv.addSpacing(20)
        self.btn_init = self._tb("dash.initialize", "btnPrimary"); self.btn_init.setFixedHeight(44); self.btn_init.setEnabled(False)
        self.btn_init.clicked.connect(self._do_setup); mv.addWidget(self.btn_init, alignment=Qt.AlignmentFlag.AlignCenter)
        # loading in a container that fills remaining space, GIF centered inside
        self._load_wrap = QWidget(main); self._load_wrap.hide()
        lw = QVBoxLayout(self._load_wrap); lw.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._load_gif = QLabel(); self._load_gif.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._load_movie = QMovie(str(Path(__file__).parent.parent.parent / "loading.gif"))
        self._load_movie.setCacheMode(QMovie.CacheMode.CacheAll); self._load_movie.setScaledSize(QSize(48,48))
        self._load_gif.setMovie(self._load_movie); lw.addWidget(self._load_gif)
        self._load_label = QLabel(""); self._load_label.setObjectName("hint"); self._load_label.setAlignment(Qt.AlignmentFlag.AlignCenter); lw.addWidget(self._load_label)
        mv.addWidget(self._load_wrap, 1)
        h.addWidget(main, 1)

    def _browse(self):
        p = QFileDialog.getExistingDirectory(self, _t("dash.select_folder"))
        if p: self.input_path.setText(p)
    def _load_repos(self):
        self.repo_list.clear(); self.repo_list.addItem(_t("dash.loading_repos"))
        self._load_thread = _LoadReposThread(); self._load_thread.finished.connect(self._on_repos_loaded)
        self._load_thread.start()
    def _on_repos_loaded(self, ok: bool, repos: list, err: str):
        self.repo_list.clear(); self._repos = repos if ok else []
        for r in self._repos:
            item = QListWidgetItem()
            w = _RepoItemWidget(r, on_rename=self._do_rename_repo, on_delete=self._do_delete_repo)
            item.setSizeHint(w.sizeHint())
            self.repo_list.addItem(item); self.repo_list.setItemWidget(item, w)
        if not ok and err: QMessageBox.warning(self, _t("dash.error"), err)
        self._try_restore_selection()
    def _try_restore_selection(self):
        saved = self._config.get("repo_full_name", "")
        for i in range(self.repo_list.count()):
            w = self.repo_list.itemWidget(self.repo_list.item(i))
            if w and w._repo.get("full_name") == saved:
                self.repo_list.setCurrentRow(i)
                self._on_repo_selected(self.repo_list.item(i))
                return
    def _on_repo_selected(self, item: QListWidgetItem):
        w = self.repo_list.itemWidget(item)
        if not w: return
        self._selected_repo = w._repo; self.input_repo.setText(w._repo["full_name"]); self.btn_init.setEnabled(True)
    def _do_new_repo(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(_t("dash.new_repo"))
        dlg.setMinimumWidth(320)
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel(_t("dash.new_repo_name")))
        edit = QLineEdit(); layout.addWidget(edit)
        cb = QCheckBox(_t("dash.new_repo_private")); cb.setChecked(True); layout.addWidget(cb)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(dlg.accept); btns.rejected.connect(dlg.reject); layout.addWidget(btns)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        name = edit.text().strip()
        if not name: return
        self.btn_new_repo.setEnabled(False)
        self._action_thread = _RepoActionThread("create", name, private=cb.isChecked())
        self._action_thread.finished.connect(lambda ok, err: self._on_repo_action_done(ok, err, name))
        self._action_thread.start()
    def _do_rename_repo(self, old_name: str):
        new_name, ok = QInputDialog.getText(self, _t("dash.rename_repo"), _t("dash.new_repo_name"), text=old_name)
        if not ok or not new_name.strip() or new_name.strip() == old_name: return
        self._action_thread = _RepoActionThread("rename", old_name, new_name.strip())
        self._action_thread.finished.connect(lambda ok, err: self._on_repo_action_done(ok, err))
        self._action_thread.start()
    def _do_delete_repo(self, name: str):
        r = QMessageBox.question(self, _t("dash.delete_repo"), _t("dash.confirm_delete_repo", name),
                                 QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
        if r != QMessageBox.StandardButton.Yes: return
        self._action_thread = _RepoActionThread("delete", name)
        self._action_thread.finished.connect(lambda ok, err: self._on_repo_action_done(ok, err))
        self._action_thread.start()
    def _on_repo_action_done(self, ok: bool, err: str, name: str = ""):
        self.btn_new_repo.setEnabled(True)
        if ok: self._load_repos()
        else: QMessageBox.critical(self, _t("dash.error"), err)
    def _do_setup(self):
        if not self._selected_repo: return
        lp = self.input_path.text().strip()
        if not lp: QMessageBox.warning(self, _t("dash.error"), _t("dash.select_folder")); return
        self.btn_init.setEnabled(False)
        self._load_label.setText(_t("dash.initializing")); self._load_wrap.show(); self._load_movie.start()
        self._setup_thread = _SetupThread(self._selected_repo["name"], lp, self._config, self._config_path)
        self._setup_thread.finished.connect(self._on_setup_finished); self._setup_thread.start()
    def _on_setup_finished(self, ok: bool, err: str):
        self._load_movie.stop(); self._load_wrap.hide(); self.btn_init.setEnabled(True)
        if ok: self.setup_done.emit()
        else: QMessageBox.critical(self, _t("dash.error"), _t("dash.setup_failed", err))
    def refresh_text(self):
        super().refresh_text()
        self.input_repo.setPlaceholderText(_t("dash.repo_placeholder"))
        self.input_path.setPlaceholderText(_t("dash.folder_placeholder"))
        self.btn_refresh_repos.setToolTip(_t("tooltip.refresh"))


class _FileItemWidget(QWidget):
    def __init__(self, name: str, is_dir: bool, on_delete, on_rename, parent=None):
        super().__init__(parent); self._name = name
        row = QHBoxLayout(); row.setContentsMargins(8, 3, 8, 3); row.setSpacing(4)
        prefix = "[D] " if is_dir else "[F] "
        self.lbl = QLabel(prefix + name); self.lbl.setStyleSheet("font-size:11px;background:transparent;")
        row.addWidget(self.lbl, 1)
        self.br = QPushButton("\u270f"); self.br.setFixedSize(22, 22)
        self.br.setStyleSheet("QPushButton{background:transparent;border:none;font-size:13px;padding:0} QPushButton:hover{background:rgba(128,128,128,0.25);border-radius:3px}")
        self.br.hide(); self.br.clicked.connect(lambda: on_rename(name)); row.addWidget(self.br)
        self.bd = QPushButton("\U0001f5d1"); self.bd.setFixedSize(22, 22)
        self.bd.setStyleSheet("QPushButton{background:transparent;border:none;font-size:13px;padding:0} QPushButton:hover{background:rgba(220,60,60,0.3);border-radius:3px}")
        self.bd.hide(); self.bd.clicked.connect(lambda: on_delete(name)); row.addWidget(self.bd)
        self.setLayout(row); self.setStyleSheet("background:transparent;")
    def enterEvent(self, e): self.br.show(); self.bd.show(); super().enterEvent(e)
    def leaveEvent(self, e): self.br.hide(); self.bd.hide(); super().leaveEvent(e)


class _AttachThread(QThread):
    """Background thread for engine attach — tolerant of remote failures."""
    finished = pyqtSignal(bool, str, object)
    engine = None
    def __init__(self, path: str, full_name: str):
        super().__init__(); self.path, self.full_name = path, full_name
    def run(self):
        try:
            e = SyncEngine(self.path, self.full_name)
            if e.is_cloned:
                try:
                    e.clone()
                except Exception as clone_err:
                    _AttachThread.engine = e
                    self.finished.emit(True, str(clone_err), e)
                    return
            _AttachThread.engine = e
            self.finished.emit(True, "", e)
        except Exception as ex:
            self.finished.emit(False, str(ex), None)

class _SyncPage(QWidget, I18nMixin):
    remote_gone = pyqtSignal()
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self._config = config; self._engine: SyncEngine | None = None
        self._sync_thread: _SyncThread | None = None; self._status_raw: dict = {}
        self._current_dir = Path(".")
        self._setup_ui(); self._attach_engine_async()

    @property
    def _root(self) -> Path: return Path(self._config.get("local_path", ""))
    @property
    def _cwd(self) -> Path: return self._root / self._current_dir

    def _nav_root(self): self._current_dir = Path("."); self._refresh_file_list()
    def _nav_up(self):
        if self._current_dir != Path("."): self._current_dir = self._current_dir.parent; self._refresh_file_list()
    def _nav_enter(self, name: str): self._current_dir = self._current_dir / name; self._refresh_file_list()

    def _setup_ui(self):
        vsplit = QSplitter(Qt.Orientation.Vertical); vsplit.setChildrenCollapsible(False)
        self._sync_stack = QStackedWidget(); self._sync_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sync_wrap = QWidget()
        swl = QVBoxLayout(sync_wrap); swl.setContentsMargins(0,0,0,0)
        swl.addStretch(1)
        sync_card = QWidget(); sync_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sc = QVBoxLayout(sync_card); sc.setSpacing(12); sc.setContentsMargins(16,12,16,12)
        self.lbl_status = QLabel(_t("dash.not_init")); self.lbl_status.setStyleSheet("font-size:13px;")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter); sc.addWidget(self.lbl_status)
        br = QHBoxLayout(); br.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_pull = self._tb("dash.pull"); self.btn_pull.setMinimumWidth(120)
        self.btn_pull.clicked.connect(lambda: self._do_sync("pull")); br.addWidget(self.btn_pull)
        self.btn_push = self._tb("dash.push", "btnPrimary"); self.btn_push.setMinimumWidth(120)
        self.btn_push.clicked.connect(lambda: self._do_sync("push")); br.addWidget(self.btn_push)
        sc.addLayout(br); swl.addWidget(sync_card, alignment=Qt.AlignmentFlag.AlignCenter)
        swl.addStretch(1)
        self._sync_stack.addWidget(sync_wrap)
        load_wrap = QWidget()
        load_wrap.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        load_wrap.mousePressEvent = lambda e: self._cancel_sync()
        lwl = QVBoxLayout(load_wrap); lwl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._loading_gif = QLabel(); self._loading_gif.setAlignment(Qt.AlignmentFlag.AlignCenter)
        from PyQt6.QtGui import QMovie
        self._loading_movie = QMovie(str(Path(__file__).parent.parent.parent / "loading.gif"))
        self._loading_movie.setCacheMode(QMovie.CacheMode.CacheAll); self._loading_movie.setScaledSize(QSize(80,80))
        self._loading_gif.setMovie(self._loading_movie); lwl.addWidget(self._loading_gif)
        self._loading_label = QLabel("Loading..."); self._loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._loading_label.setStyleSheet("color: #c9d1d9; font-size: 13px; background: transparent;")
        lwl.addWidget(self._loading_label)
        self._cancel_hint = QLabel(_t("dash.click_to_cancel")); self._cancel_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cancel_hint.setStyleSheet("color: #555c68; font-size: 11px; background: transparent;")
        lwl.addWidget(self._cancel_hint)
        self._sync_stack.addWidget(load_wrap)
        self._sync_stack.setCurrentIndex(0)
        vsplit.addWidget(self._sync_stack)
        log_wrap = QWidget(); gl = QVBoxLayout(log_wrap); gl.setContentsMargins(0,0,0,0)
        grp_log = self._tg("dash.log"); gl2 = QVBoxLayout()
        self.log_view = QPlainTextEdit(); self.log_view.setReadOnly(True); self.log_view.setMinimumHeight(40)
        gl2.addWidget(self.log_view); grp_log.setLayout(gl2); gl.addWidget(grp_log); vsplit.addWidget(log_wrap)
        hsplit = QSplitter(Qt.Orientation.Horizontal); hsplit.setChildrenCollapsible(False)
        left = QWidget(); lv = QVBoxLayout(left); lv.setContentsMargins(0,0,8,0); lv.addWidget(vsplit)
        right = QWidget(); rv = QVBoxLayout(right); rv.setContentsMargins(0,0,0,0); rv.setSpacing(0)
        grp_files = self._tg("dash.files")
        grp_files.setStyleSheet("QGroupBox{padding:12px 8px 8px 8px;padding-top:24px;}QGroupBox::title{left:8px;}")
        fl = QVBoxLayout(); fl.setContentsMargins(0,0,0,0); fl.setSpacing(2)
        nav = QHBoxLayout(); nav.setSpacing(4)
        self.btn_back = QPushButton("\u2b05"); self.btn_back.setObjectName("btnNavIcon"); self.btn_back.setFixedSize(26,26)
        self.btn_back.clicked.connect(self._nav_up); nav.addWidget(self.btn_back)
        self.btn_root = QPushButton("\u2302"); self.btn_root.setObjectName("btnNavIcon"); self.btn_root.setFixedSize(26,26)
        self.btn_root.clicked.connect(self._nav_root); nav.addWidget(self.btn_root)
        nav.addStretch()
        self.btn_refresh_files = QPushButton("\u21bb"); self.btn_refresh_files.setObjectName("btnNavIcon"); self.btn_refresh_files.setFixedSize(26, 26)
        self.btn_refresh_files.clicked.connect(self._refresh_file_list); nav.addWidget(self.btn_refresh_files)
        self.btn_add = QPushButton("+"); self.btn_add.setStyleSheet("font-size:14px;padding:2px 8px;")
        add_menu = QMenu(self)
        add_menu.addAction(_t("dash.add_file"), self._add_file)
        add_menu.addAction(_t("dash.add_folder"), self._add_folder)
        self.btn_add.setMenu(add_menu)
        nav.addWidget(self.btn_add)
        fl.addLayout(nav)
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("QListWidget{padding:0px;margin:0px;}QListWidget::item{padding:0px;margin:0px;}")
        self.file_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.file_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.file_list.setMinimumHeight(40); self.file_list.setSpacing(0)
        self.file_list.itemDoubleClicked.connect(self._on_item_double_click)
        self.file_list.setAcceptDrops(True)
        self.file_list.installEventFilter(self)
        fl.addWidget(self.file_list)
        grp_files.setLayout(fl); rv.addWidget(grp_files)
        hsplit.addWidget(left); hsplit.addWidget(right)
        hsplit.setStretchFactor(0, 3); hsplit.setStretchFactor(1, 1)
        vsplit.setSizes([140, 260])
        outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.addWidget(hsplit)
        self.setAcceptDrops(True); self.installEventFilter(self)
        self.refresh_text()
    def _attach_engine_async(self):
        path = self._config.get("local_path", ""); full = self._config.get("repo_full_name", "")
        if not path or not full:
            try:
                disk = json.loads(Path(CONFIG_DIR).expanduser().joinpath(CONFIG_FILE).read_text(encoding="utf-8"))
                path = disk.get("local_path", ""); full = disk.get("repo_full_name", "")
                self._config.update(disk)
            except Exception:
                pass
        if not path or not full:
            self._log(_t("dash.reconnect_failed", "config missing local_path/repo_full_name"))
            return
        self._sync_stack.setCurrentIndex(1)
        self._loading_label.setText(_t("dash.connecting")); self._loading_movie.start()
        self._attach_thread = _AttachThread(path, full)
        self._attach_thread.finished.connect(self._on_attach_finished)
        self._attach_thread.start()
    def _on_attach_finished(self, ok: bool, msg: str, engine):
        self._loading_movie.stop(); self._sync_stack.setCurrentIndex(0)
        if ok:
            self._engine = engine
            if self._engine and self._engine.is_cloned:
                self._refresh_status(); self._refresh_file_list()
                if msg:
                    self._log(_t("dash.reconnect_failed", msg))
                else:
                    self._log(_t("dash.reconnected"))
        else:
            self._log(_t("dash.reconnect_failed", msg))
            QTimer.singleShot(0, lambda: self.remote_gone.emit())
    def _handle_drop(self, urls: list) -> tuple[int, int]:
        """Copy dropped files/folders into _cwd. Returns (files_added, folders_added)."""
        added_files = 0; added_folders = 0
        for url in urls:
            src = Path(url.toLocalFile())
            if not src.exists(): continue
            try:
                if src.is_dir():
                    dest = self._cwd / src.name
                    shutil.copytree(src, dest)
                    if not any(dest.iterdir()): (dest / ".gitkeep").touch()
                    added_folders += 1
                else:
                    shutil.copy2(src, self._cwd / src.name)
                    added_files += 1
            except Exception as e: self._log(f"Drop failed: {e}")
        if added_files: self._log(_t("dash.files_added", added_files))
        if added_folders: self._log(_t("dash.folders_added", added_folders))
        if added_files or added_folders: self._refresh_file_list(); self._refresh_status()
        return added_files, added_folders

    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        # file_list drop
        if obj is self.file_list:
            if event.type() == QEvent.Type.DragEnter:
                if event.mimeData().hasUrls(): event.accept()
                else: event.ignore()
                return True
            elif event.type() == QEvent.Type.Drop:
                self._handle_drop(event.mimeData().urls())
                return True
        # window-level drop
        if obj is self:
            if event.type() == QEvent.Type.DragEnter:
                if event.mimeData().hasUrls(): event.acceptProposedAction()
                return True
            elif event.type() == QEvent.Type.Drop:
                self._handle_drop(event.mimeData().urls())
                return True
        return super().eventFilter(obj, event)

    def refresh_text(self):
        super().refresh_text(); self._render_status()
        self.btn_back.setToolTip(_t("tooltip.back"))
        self.btn_root.setToolTip(_t("tooltip.root"))
        self.btn_refresh_files.setToolTip(_t("tooltip.refresh"))
    def _refresh_file_list(self):
        self.file_list.clear()
        if not self._root.is_dir(): return
        try:
            entries = sorted(self._cwd.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
            for entry in entries:
                if entry.name in (".git", ".gitkeep"): continue
                item = QListWidgetItem()
                w = _FileItemWidget(entry.name, entry.is_dir(), on_delete=self._on_item_delete, on_rename=self._on_item_rename)
                if entry.is_file() and entry.stat().st_size > 100_000_000:
                    w.lbl.setStyleSheet("font-size:11px;background:transparent;color:#f85149;")
                    w.lbl.setText(w.lbl.text() + f"  ({entry.stat().st_size/1_000_000:.0f} MB)")
                item.setSizeHint(w.sizeHint())
                self.file_list.addItem(item); self.file_list.setItemWidget(item, w)
            self.file_list.updateGeometry()
            QTimer.singleShot(20, self.file_list.updateGeometry)
        except Exception: pass

    def _on_item_double_click(self, item: QListWidgetItem):
        w = self.file_list.itemWidget(item)
        if not w: return
        target = self._cwd / w._name
        if target.is_dir(): self._nav_enter(w._name)
        else: os.startfile(str(target))

    def _on_item_delete(self, name: str):
        target = self._cwd / name
        r = QMessageBox.question(self, _t("dash.confirm_delete_title"), _t("dash.confirm_delete", name),
                                 QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
        if r != QMessageBox.StandardButton.Yes: return
        try:
            if target.is_dir(): shutil.rmtree(target)
            else: target.unlink()
            self._refresh_file_list(); self._refresh_status(); self._log(_t("dash.file_deleted", name))
        except PermissionError:
            QMessageBox.warning(self, _t("dash.error"), _t("dash.delete_denied", str(target)))
        except Exception as e:
            QMessageBox.warning(self, _t("dash.error"), str(e))

    def _on_item_rename(self, old: str):
        n, ok = QInputDialog.getText(self, _t("dash.rename_file"), _t("dash.new_name"), text=old)
        if not ok or not n or n == old: return
        try:
            (self._cwd / old).rename(self._cwd / n)
            self._refresh_file_list(); self._refresh_status(); self._log(_t("dash.file_renamed", old, n))
        except Exception as e: QMessageBox.warning(self, _t("dash.error"), str(e))

    def _add_file(self):
        try:
            if not self._root.is_dir(): return
            files, _ = QFileDialog.getOpenFileNames(self, _t("dash.select_file"))
            if not files: return
            self._loading_label.setText(_t("dash.adding_files")); self._loading_movie.start()
            self._sync_stack.setCurrentIndex(1); QApplication.processEvents()
            for f in files:
                try: shutil.copy2(f, self._cwd / Path(f).name)
                except Exception as e: self._log(f"Copy failed: {e}")
            self._sync_stack.setCurrentIndex(0)
            self._refresh_file_list(); self._refresh_status(); self._log(_t("dash.files_added", len(files)))
        except Exception as e:
            self._sync_stack.setCurrentIndex(0)
            self._log(f"Add files failed: {e}")

    def _add_folder(self):
        if not self._root.is_dir(): return
        src = QFileDialog.getExistingDirectory(self, _t("dash.select_folder"))
        if not src: return
        self._loading_label.setText(_t("dash.adding_folder")); self._loading_movie.start()
        self._sync_stack.setCurrentIndex(1); QApplication.processEvents()
        try:
            dest = self._cwd / Path(src).name
            shutil.copytree(src, dest)
            if not any(dest.iterdir()): (dest / ".gitkeep").touch()
            self._sync_stack.setCurrentIndex(0)
            self._refresh_file_list(); self._refresh_status()
            self._log(_t("dash.folder_copied", Path(src).name))
        except Exception as e:
            self._sync_stack.setCurrentIndex(0)
            QMessageBox.warning(self, _t("dash.error"), str(e))

    def _do_sync(self, action: str):
        if not self._engine: return
        if action == "push":
            local = str(self._engine.local_path)
            large = [f for f in Path(local).rglob("*") if f.is_file() and ".git" not in f.parts and f.stat().st_size > 100_000_000]
            if large:
                lines = []
                for f in sorted(large, key=lambda x: x.stat().st_size, reverse=True):
                    mb = f.stat().st_size / 1_000_000
                    lines.append(f"<span style='color:#f85149'>{f.relative_to(local)}</span> ({mb:.0f} MB)")
                QMessageBox.warning(
                    self, _t("dash.lfs_title"),
                    f"{_t('dash.cannot_push')}<br><br>{'<br>'.join(lines[:15])}"
                    + (f"<br>...and {len(large)-15} more" if len(large) > 15 else "")
                )
            exclude_paths = [str(f.relative_to(local)) for f in large] if large else None
            self._run_sync(action, exclude=exclude_paths)
        else:
            self._run_sync(action)
    def _run_sync(self, action: str, exclude: list[str] | None = None):
        if not self._engine: return
        text = _t("dash.pushing") if action=="push" else _t("dash.pulling")
        self._loading_label.setText(text); self._loading_movie.start(); self._sync_stack.setCurrentIndex(1)
        self._sync_thread = _SyncThread(self._engine, action, exclude=exclude)
        self._sync_thread.finished.connect(self._on_sync_finished); self._sync_thread.start()

    def _cancel_sync(self):
        if self._sync_thread and self._sync_thread.isRunning():
            self._sync_thread.cancelled = True
            self._log(_t("dash.sync_cancelled"))
        self._sync_stack.setCurrentIndex(0)
        self.btn_pull.setEnabled(True); self.btn_push.setEnabled(True)
        self.btn_pull.setText(_t("dash.pull")); self.btn_push.setText(_t("dash.push"))

    def _on_sync_finished(self, ok: bool, msg: str):
        self._sync_stack.setCurrentIndex(0)
        self.btn_pull.setEnabled(True); self.btn_push.setEnabled(True)
        self.btn_pull.setText(_t("dash.pull")); self.btn_push.setText(_t("dash.push"))
        if ok: self._log(msg); self._refresh_status(); self._refresh_file_list()
        else:
            self._log(_t("dash.sync_failed", msg)); self.lbl_status.setText(_t("dash.sync_failed_short"))
            QMessageBox.warning(self, _t("dash.error"), msg)
        self.lbl_status.setStyleSheet("font-size:12px;")
    def _refresh_status(self):
        if not self._engine or not self._engine.is_cloned: return
        try:
            s = self._engine.get_status()
            if s.get("not_ready"): return
            self._status_raw = {
                "changed": len(s.get("changed", [])),
                "untracked": len(s.get("untracked", [])),
                "behind": s.get("behind", 0),
                "ahead": s.get("ahead", 0),
                "remote_error": s.get("remote_error", False),
            }
            self._render_status()
        except Exception as e:
            self._log(f"Status refresh failed: {e}")

    def _render_status(self):
        if not self._status_raw:
            self.lbl_status.setText(_t("dash.not_init")); self.lbl_status.setStyleSheet("font-size:12px;"); return
        parts = []
        if self._status_raw.get("changed"): parts.append(_t("dash.status_modified", self._status_raw["changed"]))
        if self._status_raw.get("untracked"): parts.append(_t("dash.status_new", self._status_raw["untracked"]))
        if not parts: parts.append(_t("dash.status_clean"))
        if self._status_raw.get("ahead"): parts.append(f"本地领先 {self._status_raw['ahead']} 提交")
        if self._status_raw.get("behind"): parts.append(_t("dash.status_behind", self._status_raw["behind"]))
        if self._status_raw.get("remote_error"): parts.append(_t("dash.status_offline"))
        self.lbl_status.setText("  |  ".join(parts))
        self.lbl_status.setStyleSheet("font-size:12px;" + ("color:#f85149;" if self._status_raw.get("remote_error") else ""))

    def _log(self, msg: str): self.log_view.appendPlainText(msg)


class DashboardWidget(QWidget, I18nMixin):
    logout = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent); self._client: GitHubClient | None = None
        d = Path(CONFIG_DIR).expanduser(); d.mkdir(parents=True, exist_ok=True)
        self._config_path = d / CONFIG_FILE
        self._config = json.loads(self._config_path.read_text(encoding="utf-8")) if self._config_path.is_file() else {}
        self._page_setup: _SetupPage | None = None; self._page_sync: _SyncPage | None = None
        self._setup_ui()
    @staticmethod
    def _make_round(pm: QPixmap, sz: int) -> QPixmap:
        s = pm.scaled(sz, sz, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        r = QPixmap(sz, sz); r.fill(Qt.GlobalColor.transparent)
        p = QPainter(r); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath(); path.addEllipse(0,0,sz,sz); p.setClipPath(path); p.drawPixmap(0,0,s); p.end()
        return r

    def _setup_ui(self):
        root = QVBoxLayout(); root.setContentsMargins(32,16,32,24)
        top = QHBoxLayout()
        self.btn_avatar = QPushButton(); self.btn_avatar.setFixedSize(40,40)
        self.btn_avatar.setFlat(True)
        self.btn_avatar.setStyleSheet("QPushButton{border:none;background:transparent;padding:0;}")
        self.btn_avatar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_avatar.clicked.connect(self._show_avatar_menu)
        top.addWidget(self.btn_avatar)
        self.btn_user = QPushButton(""); self.btn_user.setFlat(True)
        self.btn_user.setStyleSheet("QPushButton{border:none;background:transparent;font-size:14px;text-align:left;padding:0 8px;}")
        self.btn_user.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_user.clicked.connect(self._show_avatar_menu)
        top.addWidget(self.btn_user)
        top.addStretch()
        self.btn_logout = self._tb("dash.logout"); self.btn_logout.clicked.connect(self._do_logout); top.addWidget(self.btn_logout)
        root.addLayout(top)
        self._stack = QStackedWidget(); root.addWidget(self._stack, 1)
        self.setLayout(root); self.refresh_text()
    def reload(self):
        self._config = json.loads(self._config_path.read_text(encoding="utf-8")) if self._config_path.is_file() else {}
        self._init_client()
    def _init_client(self):
        if not (tok := get_token()): return
        try: self._client = GitHubClient(); self.btn_user.setText(self._client.login); self._download_avatar()
        except Exception: pass
        self._show_correct_page()
    def _show_sync_page(self):
        if self._page_sync is None:
            self._page_sync = _SyncPage(self._config); self._stack.addWidget(self._page_sync)
            self._page_sync.remote_gone.connect(self._on_remote_gone)
        self._stack.setCurrentWidget(self._page_sync)
        self._update_avatar_hint()
    def _on_remote_gone(self):
        """远端仓库已删除 — 清除配置，切回初始化页面。"""
        self._config.pop("repo_full_name", None)
        self._config_path.write_text(json.dumps(self._config, indent=2, ensure_ascii=False), encoding="utf-8")
        self._page_sync = None
        self._show_setup_page()
        QMessageBox.warning(self, _t("dash.error"), _t("dash.remote_gone"))
    def _show_correct_page(self):
        if self._config.get("repo_full_name"): self._show_sync_page()
        else: self._show_setup_page()
    def _show_setup_page(self):
        if self._page_setup is None:
            self._page_setup = _SetupPage(self._config, self._config_path)
            self._page_setup.setup_done.connect(self._show_sync_page); self._stack.addWidget(self._page_setup)
        else:
            self._page_setup._load_repos()
        self._stack.setCurrentWidget(self._page_setup)
        self._update_avatar_hint()
    def _download_avatar(self):
        if not self._client: return
        try:
            import requests as req
            from PyQt6.QtGui import QIcon
            r = req.get(self._client.avatar_url, timeout=10)
            if r.status_code == 200:
                pm = QPixmap(); pm.loadFromData(r.content)
                self.btn_avatar.setIcon(QIcon(self._make_round(pm, 36)))
                self.btn_avatar.setIconSize(QSize(36, 36))
        except Exception: pass
    def refresh_text(self):
        super().refresh_text()
        if self._page_setup: self._page_setup.refresh_text()
        if self._page_sync: self._page_sync.refresh_text()
        self._update_avatar_hint()
    def eventFilter(self, obj, event):
        return super().eventFilter(obj, event)
    def _show_avatar_menu(self):
        if self._stack.currentWidget() is self._page_sync:
            self._do_reinit()
        elif self._config.get("repo_full_name"):
            self._show_sync_page()
    def _update_avatar_hint(self):
        """根据当前页面更新头像悬停提示。"""
        if self._stack.currentWidget() is self._page_sync:
            self.btn_avatar.setToolTip(_t("dash.avatar_reinit"))
            self.btn_user.setToolTip(_t("dash.avatar_reinit"))
        elif self._config.get("repo_full_name"):
            self.btn_avatar.setToolTip(_t("dash.avatar_back"))
            self.btn_user.setToolTip(_t("dash.avatar_back"))
        else:
            self.btn_avatar.setToolTip("")
            self.btn_user.setToolTip("")
    def _do_reinit(self):
        """切换到初始化页面（不清除配置，允许返回）。"""
        self._page_sync = None
        self._show_setup_page()
    def _do_logout(self):
        r = QMessageBox.question(self, _t("dash.confirm_logout_title"), _t("dash.confirm_logout"),
                                 QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes: delete_token(); self.logout.emit()
