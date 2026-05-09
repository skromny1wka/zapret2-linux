from __future__ import annotations

from settings.mode import DEFAULT_LAUNCH_METHOD, normalize_launch_method
from ui.navigation_pages import (
    resolve_control_page_for_method,
    resolve_preset_setup_page_for_method,
    resolve_preset_raw_editor_page_for_method,
    resolve_profile_setup_page_for_method,
    resolve_zapret1_navigation_pages,
    resolve_zapret2_navigation_pages,
)
from ui.page_contracts import PageMethodName
from ui.page_names import PageName
from ui.window_adapter import ensure_page, get_loaded_page, show_page
from ui.workflows.common import (
    get_current_launch_method,
    open_preset_raw_editor_page,
)


def get_mode_context_pages(window) -> set:
    mode_context_pages = set()
    winws2_pages = resolve_zapret2_navigation_pages()
    winws1_pages = resolve_zapret1_navigation_pages()
    for page_name in (
        PageName.DPI_SETTINGS,
        winws2_pages.user_presets_page,
        winws2_pages.preset_setup_page,
        winws2_pages.preset_raw_editor_page,
        winws2_pages.profile_setup_page,
        winws1_pages.control_page,
        winws1_pages.user_presets_page,
        winws1_pages.preset_setup_page,
        winws1_pages.preset_raw_editor_page,
        winws1_pages.profile_setup_page,
    ):
        page = get_loaded_page(window, page_name)
        if page is not None:
            mode_context_pages.add(page)
    return mode_context_pages


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
    setup_page = ensure_page(window, page_name)
    if setup_page is None:
        return False

    handler = getattr(setup_page, PageMethodName.SHOW_PROFILE, None)
    if not callable(handler):
        return False

    handler(profile_key)

    if show_page_after_open:
        if not show_page(window, page_name, allow_internal=allow_internal):
            return False

    return True


def resolve_navigation_page_for_preset_setup(method: str | None) -> PageName:
    normalized = normalize_launch_method(method, default="")
    page_name = resolve_preset_setup_page_for_method(normalized)
    if page_name is None:
        return resolve_control_page_for_method(normalized)
    return page_name


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
    open_preset_raw_editor_page(
        window,
        page_name,
        preset_name,
        allow_internal=allow_internal,
    )
    return True


def redirect_to_preset_setup_page_for_method(window, method: str) -> None:
    current = None
    try:
        current = window.stackedWidget.currentWidget() if hasattr(window, "stackedWidget") else None
    except Exception:
        current = None

    mode_context_pages = get_mode_context_pages(window)

    if current is not None and current not in mode_context_pages:
        return

    show_page(
        window,
        resolve_navigation_page_for_preset_setup(method),
        allow_internal=True,
    )


def show_active_mode_control_page(window, *, allow_internal: bool) -> None:
    method = get_current_launch_method(default=DEFAULT_LAUNCH_METHOD)
    show_page(
        window,
        resolve_control_page_for_method(method),
        allow_internal=allow_internal,
    )


__all__ = [
    "get_mode_context_pages",
    "open_preset_raw_editor_for_method",
    "open_profile_setup_for_method",
    "redirect_to_preset_setup_page_for_method",
    "resolve_navigation_page_for_preset_setup",
    "show_active_mode_control_page",
]
