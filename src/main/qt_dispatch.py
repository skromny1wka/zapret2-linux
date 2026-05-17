from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import QTimer


def run_queued(callback: Callable[[], None]) -> None:
    QTimer.singleShot(0, callback)


def run_queued_with_str(callback: Callable[[str], None], value: str) -> None:
    QTimer.singleShot(0, lambda: callback(str(value or "")))
