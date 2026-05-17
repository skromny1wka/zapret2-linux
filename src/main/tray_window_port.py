from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from log.log import log
from PyQt6.QtWidgets import QInputDialog, QLineEdit
from qfluentwidgets import RoundMenu
from ui.popup_menu import exec_popup_menu
from ui.window_adapter import (
    hide_window,
    persist_window_geometry,
    release_input_interaction_states,
    request_exit,
    show_window,
)


@dataclass(frozen=True, slots=True)
class TrayWindowPort:
    """Узкий доступ трея к главному окну."""

    _window: Any

    def set_window_icon(self, icon) -> None:
        self._window.setWindowIcon(icon)

    def create_menu(self):
        return RoundMenu(parent=self._window)

    def exec_popup_menu(self, menu, position) -> None:
        exec_popup_menu(
            menu,
            position,
            owner=self._window,
            monitor_global_mouse=True,
        )

    def prompt_console_command(self):
        return QInputDialog.getText(
            self._window,
            "Консоль",
            "Введите команду:",
            QLineEdit.EchoMode.Normal,
            "",
        )

    def is_visible(self) -> bool:
        try:
            return bool(self._window.isVisible())
        except Exception:
            return False

    def persist_geometry(self) -> None:
        try:
            persist_window_geometry(self._window)
        except Exception as exc:
            log(f"Ошибка сохранения геометрии окна: {exc}", "ERROR")

    def release_input_interaction_states(self) -> None:
        release_input_interaction_states(self._window)

    def hide(self) -> None:
        hide_window(self._window)

    def show(self) -> None:
        show_window(self._window)

    def request_exit(self, *, stop_dpi: bool) -> None:
        request_exit(self._window, stop_dpi=bool(stop_dpi))


def build_tray_window_port(window) -> TrayWindowPort:
    return TrayWindowPort(window)


__all__ = ["TrayWindowPort", "build_tray_window_port"]
