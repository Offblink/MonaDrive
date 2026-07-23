"""Loading overlay -- GitHub loading spinner (mona)."""

from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class LoadingOverlay(QWidget):
    """Semi-transparent overlay with GitHub loading animation."""

    _GIF_PATH = Path(__file__).parent.parent.parent / "loading.gif"

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setStyleSheet("background: #0a0e14;")
        self.hide()
        parent.installEventFilter(self)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._movie = QMovie(str(self._GIF_PATH))
        self._movie.setCacheMode(QMovie.CacheMode.CacheAll)
        self._movie.setScaledSize(QSize(80, 80))

        self._gif = QLabel()
        self._gif.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._gif.setMovie(self._movie)
        layout.addWidget(self._gif)

        self._msg = QLabel("Loading...")
        self._msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._msg.setStyleSheet("color: #c9d1d9; font-size: 13px; background: transparent;")
        layout.addWidget(self._msg)
        layout.addStretch()
        self.setLayout(layout)

    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        if obj is self.parent() and event.type() == QEvent.Type.Resize:
            self._cover_parent()
        return super().eventFilter(obj, event)

    def show_message(self, text: str):
        self._msg.setText(text)
        self._movie.start()
        self._cover_parent()
        self.show()
        self.raise_()

    def _cover_parent(self):
        p = self.parent()
        if p: self.setGeometry(0, 0, p.width(), p.height())

    def showEvent(self, event):
        self._cover_parent()
        super().showEvent(event)
