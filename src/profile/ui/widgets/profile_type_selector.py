# profile/ui/widgets/profile_type_selector.py
"""
Кнопки выбора типа профиля/трафика в списке профилей.
Поддерживает множественный выбор (не exclusive).
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtCore import pyqtSignal

try:
    from qfluentwidgets import PillPushButton
    _HAS_FLUENT = True
except ImportError:
    from PyQt6.QtWidgets import QPushButton as PillPushButton  # type: ignore[assignment]
    _HAS_FLUENT = False


class _ProfileTypeButton(PillPushButton):
    """PillPushButton с привязанным ключом типа профиля."""

    def __init__(self, label: str, profile_type: str, parent=None):
        super().__init__(parent)
        self.setText(label)
        self._profile_type = profile_type
        self.setCheckable(True)

    @property
    def profile_type(self) -> str:
        return self._profile_type


class ProfileTypeSelector(QWidget):
    """
    Группа кнопок для выбора типа профиля/трафика в списке профилей.

    Множественный выбор (не exclusive):
    - "Все" снимает остальные типы;
    - выбор других типов снимает "Все";
    - можно комбинировать TCP + Discord и т.д.

    Signals:
        profile_types_changed(set): Эмитит set активных типов профиля.
    """

    profile_types_changed = pyqtSignal(set)

    PROFILE_TYPES = [
        ("all",     "Все"),
        ("tcp",     "TCP"),
        ("udp",     "UDP"),
        ("discord", "Discord"),
        ("voice",   "Voice"),
        ("games",   "Games"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._buttons: dict[str, _ProfileTypeButton] = {}
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(6)

        for profile_type, label in self.PROFILE_TYPES:
            btn = _ProfileTypeButton(label, profile_type, self)
            btn.clicked.connect(self._on_button_clicked)
            self._buttons[profile_type] = btn
            layout.addWidget(btn)

            if profile_type == "all":
                btn.setChecked(True)

        layout.addStretch()

    def _on_button_clicked(self):
        sender = self.sender()
        if not isinstance(sender, _ProfileTypeButton):
            return

        clicked_key = sender.profile_type
        is_checked = sender.isChecked()

        if clicked_key == "all":
            if is_checked:
                for key, btn in self._buttons.items():
                    if key != "all":
                        btn.setChecked(False)
            else:
                if not self._has_other_selected():
                    sender.setChecked(True)
        else:
            if is_checked:
                self._buttons["all"].setChecked(False)
            else:
                if not self._has_other_selected():
                    self._buttons["all"].setChecked(True)

        self.profile_types_changed.emit(self.get_active_profile_types())

    def _has_other_selected(self) -> bool:
        for key, btn in self._buttons.items():
            if key != "all" and btn.isChecked():
                return True
        return False

    def get_active_profile_types(self) -> set:
        return {key for key, btn in self._buttons.items() if btn.isChecked()}

    def set_active_profile_types(self, profile_types: set):
        self.blockSignals(True)
        for key, btn in self._buttons.items():
            btn.setChecked(key in profile_types)
        if not profile_types or not self._has_other_selected():
            self._buttons["all"].setChecked(True)
            for key, btn in self._buttons.items():
                if key != "all":
                    btn.setChecked(False)
        self.blockSignals(False)

    def reset(self):
        self.set_active_profile_types({"all"})
        self.profile_types_changed.emit({"all"})
