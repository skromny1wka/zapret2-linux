from __future__ import annotations

from dataclasses import dataclass
import sys
from typing import Callable


@dataclass(frozen=True, slots=True)
class GuiAutostartResult:
    success: bool
    removed_count: int = 0
    restart_requested: bool = False
    message: str = ""


def get_current_launch_method() -> str:
    from settings.dpi.public import get_launch_method

    return str(get_launch_method() or "").strip()


def save_gui_autostart_enabled(enabled: bool) -> bool:
    from settings.store import set_gui_autostart_enabled

    return bool(set_gui_autostart_enabled(bool(enabled)))


def disable_gui_autostart() -> GuiAutostartResult:
    from autostart.startup_shortcut_api import delete_startup_shortcut

    removed_count = 1 if delete_startup_shortcut() else 0
    return GuiAutostartResult(success=True, removed_count=removed_count)


def enable_gui_autostart(*, status_cb: Callable[[str], None] | None = None) -> GuiAutostartResult:
    from autostart.startup_shortcut_api import create_or_update_startup_shortcut, delete_startup_shortcut

    def _status(message: str) -> None:
        if status_cb is not None:
            status_cb(message)

    try:
        _status("Удаление старого ярлыка автозапуска...")
        delete_startup_shortcut()
        _status("Создание ярлыка автозапуска...")
        ok = bool(create_or_update_startup_shortcut(sys.executable))
    except Exception:
        ok = False
    if ok:
        _status("Автозапуск программы включён")
        return GuiAutostartResult(success=True)
    return GuiAutostartResult(
        success=False,
        message=(
            "Не удалось включить автозапуск. Windows не дал создать ярлык "
            "в папке автозагрузки."
        ),
    )


__all__ = [
    "GuiAutostartResult",
    "disable_gui_autostart",
    "enable_gui_autostart",
    "get_current_launch_method",
    "save_gui_autostart_enabled",
]
