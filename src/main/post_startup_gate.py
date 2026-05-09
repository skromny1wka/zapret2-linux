from __future__ import annotations

from PyQt6.QtCore import QTimer


def is_window_alive(window) -> bool:
    return not bool(
        getattr(window, "_is_exiting", False)
        or getattr(window, "_closing_completely", False)
    )


def bind_startup_gate(signal, callback, *, is_ready) -> None:
    started = False

    def _run(*_args) -> None:
        nonlocal started
        if started:
            return
        started = True
        callback()

    try:
        signal.connect(_run)
    except Exception:
        QTimer.singleShot(0, _run)
        return

    try:
        if bool(is_ready()):
            QTimer.singleShot(0, _run)
    except Exception:
        QTimer.singleShot(0, _run)
