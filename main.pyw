"""MonaDrive — GitHub-powered private cloud drive.

启动时自动检测依赖，缺则 pip install -r requirements.txt 后重启。
单实例：重复启动会唤醒已有窗口到前台。
"""

import importlib
import subprocess
import sys
from pathlib import Path


def _ensure_deps() -> None:
    _REQUIREMENTS = Path(__file__).parent / "requirements.txt"
    if not _REQUIREMENTS.is_file():
        return
    _PKG_MOD = (
        ("PyQt6", "PyQt6"), ("PyGithub", "github"), ("GitPython", "git"),
        ("watchdog", "watchdog"), ("keyring", "keyring"), ("requests", "requests"),
    )
    missing = []
    for pkg, mod in _PKG_MOD:
        try:
            importlib.import_module(mod)
        except ImportError:
            missing.append(pkg)
    if not missing:
        return
    print(f"MonaDrive: 检测到缺失依赖 -> {', '.join(missing)}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(_REQUIREMENTS)])
    except Exception as e:
        print(f"自动安装失败: {e}\n请手动运行: pip install -r requirements.txt")
        sys.exit(1)
    print("依赖安装完成，请重新启动 MonaDrive。")
    sys.exit(0)


_ensure_deps()

from PyQt6.QtCore import QSharedMemory
from PyQt6.QtNetwork import QLocalSocket
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.gui.themes import load_fonts


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MonaDrive")
    app.setOrganizationName("MonaDrive")
    app.setStyle("Fusion")
    app.setQuitOnLastWindowClosed(False)

    # ── 单实例：重复启动则唤醒已有窗口 ──
    shared = QSharedMemory("MonaDriveSingleton")
    if shared.attach() or not shared.create(1):
        sock = QLocalSocket()
        sock.connectToServer("MonaDriveIPC")
        if sock.waitForConnected(500):
            sock.disconnectFromServer()
        sys.exit(0)

    load_fonts()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
