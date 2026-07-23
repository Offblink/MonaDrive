"""MonaDrive QSS themes — dark + light, taste-skill v2 design tokens."""

from pathlib import Path
from PyQt6.QtGui import QFontDatabase

FONT = "'Monocraft', 'Cascadia Code', 'Consolas', monospace"


def load_fonts():
    font_path = Path(__file__).parent.parent.parent / "Monocraft.ttf"
    if not font_path.exists():
        return None
    fid = QFontDatabase.addApplicationFont(str(font_path))
    if fid >= 0:
        families = QFontDatabase.applicationFontFamilies(fid)
        return families[0] if families else None
    return None


DARK = f"""
QWidget {{
    background-color: #0a0e14;
    color: #c9d1d9;
    font-family: {FONT};
    font-size: 13px;
    selection-background-color: #1f3329;
    selection-color: #e6edf3;
}}

QWidget#repoSidebar {{ background-color: #0d1117; border-right: 1px solid #1e2430; }}
QMainWindow {{ background-color: #0a0e14; }}

QPushButton {{
    background-color: #12161c;
    color: #c9d1d9;
    border: 1px solid #1e2430;
    border-radius: 4px;
    padding: 10px 24px;
    font-size: 13px;
}}
QPushButton:hover {{ background-color: #181d25; border-color: #2a3340; }}
QPushButton:pressed {{ background-color: #0a0e14; }}
QPushButton:disabled {{ background-color: #0d1117; color: #3a414d; border-color: #161b22; }}

QPushButton#btnPrimary {{
    background-color: #1f402b;
    color: #e6edf3;
    border: 1px solid #2b5a3a;
}}
QPushButton#btnPrimary:hover {{ background-color: #2b5a3a; border-color: #3fb950; }}
QPushButton#btnPrimary:pressed {{ background-color: #1a3322; }}
QPushButton#btnPrimary:disabled {{ background-color: #0d1a13; color: #1f402b; border-color: #122218; }}

QPushButton#btnDanger {{
    background-color: #3d1f1f;
    color: #e6edf3;
    border: 1px solid #5c2b2b;
}}
QPushButton#btnDanger:hover {{ background-color: #5c2b2b; border-color: #f85149; }}

QPushButton#btnIcon {{
    background: transparent;
    border: 1px solid #1e2430;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 16px;
    min-width: 36px;
    min-height: 36px;
}}
QPushButton#btnIcon:hover {{ background-color: #181d25; }}

QPushButton#btnNavIcon {{
    background: transparent;
    border: none;
    font-size: 14px;
    padding: 0;
}}
QPushButton#btnNavIcon:hover {{ background-color: #30363d; border-radius: 3px; }}

QLabel {{ color: #c9d1d9; background: transparent; border: none; }}
QLabel#heading {{ font-size: 24px; color: #e6edf3; }}
QLabel#subheading {{ font-size: 15px; color: #7a8290; }}
QLabel#statusOk  {{ color: #3fb950; }}
QLabel#statusWarn {{ color: #d29922; }}
QLabel#statusErr  {{ color: #f85149; }}
QLabel#hint {{ font-size: 11px; color: #555c68; }}

QLineEdit {{
    background-color: #0a0e14;
    color: #c9d1d9;
    border: 1px solid #1e2430;
    border-radius: 4px;
    padding: 10px 14px;
    font-size: 13px;
}}
QLineEdit:focus {{ border-color: #3fb950; background-color: #0d1218; }}
QLineEdit:disabled {{ background-color: #0d1117; color: #3a414d; }}
QLineEdit::placeholder {{ color: #3a414d; }}

QTextEdit, QPlainTextEdit {{
    background-color: #0a0e14;
    color: #c9d1d9;
    border: 1px solid #1e2430;
    border-radius: 4px;
    padding: 10px;
    font-size: 11px;
}}
QTextEdit:focus, QPlainTextEdit:focus {{ border-color: #3fb950; }}

QGroupBox {{
    border: 1px solid #1e2430;
    border-radius: 4px;
    margin-top: 22px;
    padding: 28px 24px 20px 24px;
    font-size: 13px;
    color: #7a8290;
    font-weight: normal;
}}
QGroupBox::title {{ subcontrol-origin: margin; left: 16px; padding: 0 8px; color: #7a8290; }}

QScrollBar:vertical {{ background: #0a0e14; width: 8px; margin: 0; }}
QScrollBar::handle:vertical {{ background: #1e2430; border-radius: 4px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: #2a3340; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

QToolTip {{
    background-color: #12161c;
    color: #c9d1d9;
    border: 1px solid #1e2430;
    border-radius: 4px;
    padding: 8px;
    font-size: 11px;
}}

QListWidget {{ background-color: #0a0e14; border: 1px solid #1e2430; border-radius: 4px; outline: none; }}
QListWidget::item {{ padding: 6px 12px; }}
QListWidget::item:selected {{ background-color: #12161c; color: #e6edf3; }}

QProgressBar {{ border: 1px solid #1e2430; border-radius: 4px; background-color: #0a0e14; text-align: center; color: #c9d1d9; font-size: 10px; height: 6px; }}
QProgressBar::chunk {{ background-color: #3fb950; border-radius: 3px; }}
"""

LIGHT = f"""
QWidget {{
    background-color: #f6f8fa;
    color: #1f2328;
    font-family: {FONT};
    font-size: 13px;
    selection-background-color: #ddf4e0;
    selection-color: #1f2328;
}}
QMainWindow {{ background-color: #f6f8fa; }}

QWidget#repoSidebar {{ background-color: #ffffff; border-right: 1px solid #d0d7de; }}

QPushButton {{
    background-color: #f6f8fa;
    color: #1f2328;
    border: 1px solid #d0d7de;
    border-radius: 4px;
    padding: 10px 24px;
    font-size: 13px;
}}
QPushButton:hover {{ background-color: #eaeef2; border-color: #afb8c1; }}
QPushButton:pressed {{ background-color: #dde3ea; }}
QPushButton:disabled {{ background-color: #f3f4f6; color: #8c959f; border-color: #e1e4e8; }}

QPushButton#btnPrimary {{
    background-color: #1f883d;
    color: #ffffff;
    border: 1px solid #1f883d;
}}
QPushButton#btnPrimary:hover {{ background-color: #1a7a35; border-color: #187733; }}
QPushButton#btnPrimary:pressed {{ background-color: #166b2e; }}
QPushButton#btnPrimary:disabled {{ background-color: #94d3a2; color: #ffffff; border-color: #94d3a2; }}

QPushButton#btnDanger {{
    background-color: #cf222e;
    color: #ffffff;
    border: 1px solid #cf222e;
}}
QPushButton#btnDanger:hover {{ background-color: #a40e26; }}

QPushButton#btnIcon {{
    background: transparent;
    border: 1px solid #d0d7de;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 16px;
    min-width: 36px;
    min-height: 36px;
}}
QPushButton#btnIcon:hover {{ background-color: #eaeef2; }}

QPushButton#btnNavIcon {{
    background: transparent;
    border: none;
    font-size: 14px;
    padding: 0;
}}
QPushButton#btnNavIcon:hover {{ background-color: #eaeef2; border-radius: 3px; }}

QLabel {{ color: #1f2328; background: transparent; border: none; }}
QLabel#heading {{ font-size: 24px; color: #0d1117; }}
QLabel#subheading {{ font-size: 15px; color: #656d76; }}
QLabel#statusOk  {{ color: #1a7f37; }}
QLabel#statusWarn {{ color: #9a6700; }}
QLabel#statusErr  {{ color: #cf222e; }}
QLabel#hint {{ font-size: 11px; color: #656d76; }}

QLineEdit {{
    background-color: #ffffff;
    color: #1f2328;
    border: 1px solid #d0d7de;
    border-radius: 4px;
    padding: 10px 14px;
    font-size: 13px;
}}
QLineEdit:focus {{ border-color: #1f883d; background-color: #ffffff; }}
QLineEdit:disabled {{ background-color: #f3f4f6; color: #8c959f; }}
QLineEdit::placeholder {{ color: #8c959f; }}

QTextEdit, QPlainTextEdit {{
    background-color: #ffffff;
    color: #1f2328;
    border: 1px solid #d0d7de;
    border-radius: 4px;
    padding: 10px;
    font-size: 11px;
}}
QTextEdit:focus, QPlainTextEdit:focus {{ border-color: #1f883d; }}

QGroupBox {{
    border: 1px solid #d0d7de;
    border-radius: 4px;
    margin-top: 22px;
    padding: 28px 24px 20px 24px;
    font-size: 13px;
    color: #656d76;
    font-weight: normal;
}}
QGroupBox::title {{ subcontrol-origin: margin; left: 16px; padding: 0 8px; color: #374151; }}

QScrollBar:vertical {{ background: #f6f8fa; width: 8px; margin: 0; }}
QScrollBar::handle:vertical {{ background: #d0d7de; border-radius: 4px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: #afb8c1; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

QToolTip {{
    background-color: #ffffff;
    color: #1f2328;
    border: 1px solid #d0d7de;
    border-radius: 4px;
    padding: 8px;
    font-size: 11px;
}}

QListWidget {{ background-color: #ffffff; border: 1px solid #d0d7de; border-radius: 4px; outline: none; }}
QListWidget::item {{ padding: 6px 12px; }}
QListWidget::item:selected {{ background-color: #ddf4e0; color: #0d1117; }}

QProgressBar {{ border: 1px solid #d0d7de; border-radius: 4px; background-color: #ffffff; text-align: center; color: #1f2328; font-size: 10px; height: 6px; }}
QProgressBar::chunk {{ background-color: #1f883d; border-radius: 3px; }}
"""


def get_theme(dark: bool) -> str:
    return DARK if dark else LIGHT
