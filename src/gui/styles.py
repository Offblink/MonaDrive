"""MonaDrive QSS — dark tech / monospace aesthetic. Taste-skill v2 redesign.

Design tokens:
  Surface:  #0a0e14  (deep blue-black)
  Raised:   #12161c
  Border:   #1e2430
  Text:     #c9d1d9
  Muted:    #7a8290
  Accent:   #3fb950  (emerald, not AI-purple)
  Danger:   #f85149
  Radius:   4px uniform
"""

from pathlib import Path

from PyQt6.QtGui import QFontDatabase

FONT_SIZE_SM = "11px"
FONT_SIZE    = "13px"
FONT_SIZE_LG = "15px"

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


# Language-borrowed from taste-skill: one accent, one page theme, no glow, no gradient
STYLESHEET = f"""
/* ================================================================
   GLOBAL
   ================================================================ */
QWidget {{
    background-color: #0a0e14;
    color: #c9d1d9;
    font-family: {FONT};
    font-size: {FONT_SIZE};
    selection-background-color: #1f3329;
    selection-color: #e6edf3;
}}

/* ================================================================
   WINDOW
   ================================================================ */
QMainWindow {{
    background-color: #0a0e14;
}}

/* ================================================================
   BUTTON
   ================================================================ */
QPushButton {{
    background-color: #12161c;
    color: #c9d1d9;
    border: 1px solid #1e2430;
    border-radius: 4px;
    padding: 10px 24px;
    font-size: {FONT_SIZE};
}}
QPushButton:hover {{
    background-color: #181d25;
    border-color: #2a3340;
}}
QPushButton:pressed {{
    background-color: #0a0e14;
}}
QPushButton:disabled {{
    background-color: #0d1117;
    color: #3a414d;
    border-color: #161b22;
}}

QPushButton#btnPrimary {{
    background-color: #1f402b;
    color: #e6edf3;
    border: 1px solid #2b5a3a;
}}
QPushButton#btnPrimary:hover {{
    background-color: #2b5a3a;
    border-color: #3fb950;
}}
QPushButton#btnPrimary:pressed {{
    background-color: #1a3322;
}}
QPushButton#btnPrimary:disabled {{
    background-color: #0d1a13;
    color: #1f402b;
    border-color: #122218;
}}

QPushButton#btnDanger {{
    background-color: #3d1f1f;
    color: #e6edf3;
    border: 1px solid #5c2b2b;
}}
QPushButton#btnDanger:hover {{
    background-color: #5c2b2b;
    border-color: #f85149;
}}
QPushButton#btnDanger:pressed {{
    background-color: #2d1515;
}}

/* ================================================================
   LABEL
   ================================================================ */
QLabel {{
    color: #c9d1d9;
    background: transparent;
    border: none;
}}
QLabel#heading {{
    font-size: 24px;
    color: #e6edf3;
}}
QLabel#subheading {{
    font-size: {FONT_SIZE_LG};
    color: #7a8290;
}}
QLabel#statusOk  {{ color: #3fb950; }}
QLabel#statusWarn {{ color: #d29922; }}
QLabel#statusErr  {{ color: #f85149; }}
QLabel#hint {{
    font-size: {FONT_SIZE_SM};
    color: #555c68;
}}

/* ================================================================
   INPUT
   ================================================================ */
QLineEdit {{
    background-color: #0a0e14;
    color: #c9d1d9;
    border: 1px solid #1e2430;
    border-radius: 4px;
    padding: 10px 14px;
    font-size: {FONT_SIZE};
}}
QLineEdit:focus {{
    border-color: #3fb950;
    background-color: #0d1218;
}}
QLineEdit:disabled {{
    background-color: #0d1117;
    color: #3a414d;
}}
QLineEdit::placeholder {{
    color: #3a414d;
}}

/* ================================================================
   TEXT AREA
   ================================================================ */
QTextEdit, QPlainTextEdit {{
    background-color: #0a0e14;
    color: #c9d1d9;
    border: 1px solid #1e2430;
    border-radius: 4px;
    padding: 10px;
    font-size: {FONT_SIZE_SM};
}}
QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: #3fb950;
}}

/* ================================================================
   GROUP BOX
   ================================================================ */
QGroupBox {{
    border: 1px solid #1e2430;
    border-radius: 4px;
    margin-top: 20px;
    padding: 24px 20px 16px 20px;
    font-size: {FONT_SIZE};
    color: #7a8290;
    font-weight: normal;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    color: #7a8290;
}}

/* ================================================================
   SCROLLBAR
   ================================================================ */
QScrollBar:vertical {{
    background: #0a0e14;
    width: 8px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: #1e2430;
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: #2a3340;
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* ================================================================
   TOOLTIP
   ================================================================ */
QToolTip {{
    background-color: #12161c;
    color: #c9d1d9;
    border: 1px solid #1e2430;
    border-radius: 4px;
    padding: 8px;
    font-size: {FONT_SIZE_SM};
}}

/* ================================================================
   LIST
   ================================================================ */
QListWidget {{
    background-color: #0a0e14;
    border: 1px solid #1e2430;
    border-radius: 4px;
    outline: none;
}}
QListWidget::item {{
    padding: 6px 12px;
}}
QListWidget::item:selected {{
    background-color: #12161c;
    color: #e6edf3;
}}

/* ================================================================
   PROGRESS
   ================================================================ */
QProgressBar {{
    border: 1px solid #1e2430;
    border-radius: 4px;
    background-color: #0a0e14;
    text-align: center;
    color: #c9d1d9;
    font-size: 10px;
    height: 6px;
}}
QProgressBar::chunk {{
    background-color: #3fb950;
    border-radius: 3px;
}}
"""
