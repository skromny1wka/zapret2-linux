from __future__ import annotations

from log.log import log
from ui.navigation_pages import (
    resolve_preset_raw_editor_page_for_method,
    resolve_preset_setup_page_for_method,
    resolve_profile_setup_page_for_method,
)
from ui.window_adapter import send_page_command, show_page


def open_profile_setup_for_method(
    window,
    method: str | None,
    profile_key: str,
    *,
    show_page_after_open: bool = True,
    allow_internal: bool = False,
) -> bool:
    page_name = resolve_profile_setup_page_for_method(method)
    if page_name is None:
        return False
    if not send_page_command(
        window,
        page_name,
        "open_profile",
        {"profile_key": profile_key},
        ensure=True,
    ):
        log("Не удалось открыть profile setup: страница не приняла команду", "ERROR")
        return False

    if show_page_after_open:
        return bool(show_page(window, page_name, allow_internal=allow_internal))
    return True


def open_preset_raw_editor_for_method(
    window,
    method: str | None,
    preset_name: str,
    *,
    allow_internal: bool,
) -> bool:
    page_name = resolve_preset_raw_editor_page_for_method(method)
    if page_name is None:
        return False
    if not send_page_command(
        window,
        page_name,
        "open_raw_preset",
        {"preset_name": preset_name},
        ensure=True,
    ):
        log("Не удалось открыть raw preset editor: страница не приняла команду", "ERROR")
        return False

    return bool(show_page(window, page_name, allow_internal=allow_internal))


def apply_profile_setup_change_for_method(
    window,
    method: str,
    profile_key: str,
    change_kind: str,
) -> bool:
    preset_setup_page = resolve_preset_setup_page_for_method(method)
    if preset_setup_page is None:
        return False
    return send_page_command(
        window,
        preset_setup_page,
        "profile_setup_changed",
        {"profile_key": profile_key, "change_kind": change_kind},
        ensure=False,
    )


__all__ = [
    "apply_profile_setup_change_for_method",
    "open_preset_raw_editor_for_method",
    "open_profile_setup_for_method",
]
