from __future__ import annotations

import time

from app_notifications import advisory_notification, notification_action
from log.log import log


class RuntimeUiBridge:
    """Единый runtime -> UI bridge без знания главного окна."""

    def __init__(self, *, notify, set_status, mark_content_changed):
        self._notify = notify
        self._set_status = set_status
        self._mark_content_changed = mark_content_changed
        self._last_content_change_key = ""
        self._last_content_change_at = 0.0

    def set_status(self, text: str) -> None:
        callback = self._set_status
        if not callable(callback):
            raise RuntimeError("RuntimeUiBridge requires set_status callback")
        callback(str(text or ""))

    def show_launch_error(self, message: str) -> None:
        text = str(message or "").strip()
        if not text:
            return
        try:
            while text.startswith(("❌", "⚠️", "⚠")):
                text = text[1:].strip()
        except Exception:
            pass
        if not text:
            text = "Не удалось запустить DPI"

        try:
            auto_fix_action = None
            if text.startswith("[AUTOFIX:"):
                end_idx = text.find("]")
                if end_idx > 0:
                    auto_fix_action = text[9:end_idx]
                    text = text[end_idx + 1 :].strip()

            buttons = []
            duration = 10000
            if auto_fix_action:
                buttons.append(notification_action("autofix", "Исправить", value=auto_fix_action))
                duration = -1

            self._notify(
                advisory_notification(
                    level="error",
                    title="Ошибка",
                    content=text,
                    source="launch.dpi_error",
                    presentation="infobar",
                    queue="immediate",
                    duration=duration,
                    buttons=buttons,
                    dedupe_key=f"launch.dpi_error:{' '.join(text.split()).lower()}",
                )
            )
        except Exception as e:
            log(f"Не удалось показать InfoBar ошибки запуска: {e}", "DEBUG")

    def show_launch_warning(self, message: str) -> None:
        text = str(message or "").strip()
        if not text:
            return
        try:
            while text.startswith(("⚠️", "⚠")):
                text = text[1:].strip()
        except Exception:
            pass
        if not text:
            return

        try:
            self._notify(
                advisory_notification(
                    level="warning",
                    title="Предупреждение",
                    content=text,
                    source="launch.dpi_warning",
                    presentation="infobar",
                    queue="immediate",
                    duration=9000,
                    dedupe_key=f"launch.dpi_warning:{' '.join(text.split()).lower()}",
                )
            )
        except Exception as e:
            log(f"Не удалось показать InfoBar предупреждения запуска: {e}", "DEBUG")

    def handle_runtime_content_changed(self, key: str) -> None:
        normalized_key = str(key or "").strip().lower()
        if not normalized_key:
            return

        now = time.monotonic()
        if (
            normalized_key == self._last_content_change_key
            and (now - self._last_content_change_at) < 0.5
        ):
            return

        self._last_content_change_key = normalized_key
        self._last_content_change_at = now

        try:
            self._mark_content_changed()
        except Exception:
            pass


__all__ = ["RuntimeUiBridge"]
