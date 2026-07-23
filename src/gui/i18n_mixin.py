"""i18n-aware widget base — unified translation tracking for all pages."""

from PyQt6.QtWidgets import QGroupBox, QLabel, QPushButton, QCheckBox, QSizePolicy
from src.gui.i18n import t as _t


class I18nMixin:
    """Mixin that provides _tl / _tb / _tg helpers with automatic registration.

    Subclasses call self._tl(key, ...) instead of QLabel(_t(key)),
    then self.refresh_text() will update everything in one pass.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Per-instance lists, not class-level
        orig_init = cls.__init__

        def new_init(self, *a, **kw):
            self._i18n_labels: list[tuple[QLabel, str, tuple]] = []
            self._i18n_buttons: list[tuple[QPushButton, str]] = []
            self._i18n_groups: list[tuple[QGroupBox, str]] = []
            self._i18n_checkboxes: list[tuple[QCheckBox, str]] = []
            orig_init(self, *a, **kw)
        cls.__init__ = new_init

    def _tl(self, key: str, *args, css: str = "") -> QLabel:
        """Create a tracked translatable QLabel."""
        lbl = QLabel(_t(key, *args) if args else _t(key))
        if css:
            lbl.setStyleSheet(css)
        self._i18n_labels.append((lbl, key, args))
        return lbl

    def _tb(self, key: str, obj_name: str = "") -> QPushButton:
        """Create a tracked translatable QPushButton."""
        btn = QPushButton(_t(key))
        if obj_name:
            btn.setObjectName(obj_name)
        btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self._i18n_buttons.append((btn, key))
        return btn

    def _tg(self, key: str) -> QGroupBox:
        """Create a tracked translatable QGroupBox."""
        grp = QGroupBox(_t(key))
        self._i18n_groups.append((grp, key))
        return grp

    def _tc(self, key: str) -> QCheckBox:
        """Create a tracked translatable QCheckBox."""
        cb = QCheckBox(_t(key))
        cb.setChecked(True)
        cb.setStyleSheet("font-size: 12px;")
        self._i18n_checkboxes.append((cb, key))
        return cb

    def refresh_text(self):
        """Re-apply all translations to tracked widgets.

        Override in subclasses to handle additional untracked widgets
        (placeholder text, dynamic labels, etc.).
        """
        for lbl, key, args in self._i18n_labels:
            lbl.setText(_t(key, *args) if args else _t(key))
        for btn, key in self._i18n_buttons:
            btn.setText(_t(key))
        for grp, key in self._i18n_groups:
            grp.setTitle(_t(key))
        for cb, key in self._i18n_checkboxes:
            cb.setText(_t(key))
