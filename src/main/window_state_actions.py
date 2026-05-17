from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from log.log import log
from ui.window_appearance_state import (
    apply_garland_enabled,
    apply_snowflakes_enabled,
    apply_window_opacity_value,
)


@dataclass(frozen=True, slots=True)
class WindowStateActions:
    window: Any
    ui_state_store: Any

    def set_garland_enabled(self, enabled: bool) -> None:
        try:
            snapshot = self.ui_state_store.snapshot()
            self.ui_state_store.set_holiday_overlays(bool(enabled), snapshot.snowflakes_enabled)
            apply_garland_enabled(self.window, bool(enabled))
        except Exception as exc:
            log(f"❌ Ошибка переключения гирлянды: {exc}", "ERROR")

    def set_snowflakes_enabled(self, enabled: bool) -> None:
        try:
            snapshot = self.ui_state_store.snapshot()
            self.ui_state_store.set_holiday_overlays(snapshot.garland_enabled, bool(enabled))
            apply_snowflakes_enabled(self.window, bool(enabled))
        except Exception as exc:
            log(f"❌ Ошибка переключения снежинок: {exc}", "ERROR")

    def set_window_opacity(self, value: int) -> None:
        try:
            self.ui_state_store.set_window_opacity_value(value)
            apply_window_opacity_value(self.window, value)
        except Exception as exc:
            log(f"❌ Ошибка при установке прозрачности окна: {exc}", "ERROR")


__all__ = ["WindowStateActions"]
