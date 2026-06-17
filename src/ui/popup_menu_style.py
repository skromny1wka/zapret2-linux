from __future__ import annotations

import sys


def _is_windows_11_or_newer() -> bool:
    try:
        return sys.platform == "win32" and sys.getwindowsversion().build >= 22000
    except Exception:
        return False


def _round_menu_hairline_border_qss() -> str:
    try:
        from qfluentwidgets import isDarkTheme

        is_light = not isDarkTheme()
    except Exception:
        is_light = False

    if is_light:
        return "MenuActionListWidget { border-color: rgba(0, 0, 0, 0.06); }"

    return "MenuActionListWidget { border-color: rgba(255, 255, 255, 0.00); }"


def suppress_round_menu_hairline(menu) -> None:
    """Убирает только Win11-артефакт 1px по краю, не трогая стиль меню."""

    if menu is None:
        return
    if not _is_windows_11_or_newer():
        return

    qss = _round_menu_hairline_border_qss()

    try:
        current = str(menu.styleSheet() or "")
        if qss not in current:
            menu.setStyleSheet(f"{current}\n{qss}".strip())
    except Exception:
        pass

    view = getattr(menu, "view", None)
    if view is not None:
        try:
            current = str(view.styleSheet() or "")
            if qss not in current:
                view.setStyleSheet(f"{current}\n{qss}".strip())
        except Exception:
            pass


__all__ = ["suppress_round_menu_hairline"]
