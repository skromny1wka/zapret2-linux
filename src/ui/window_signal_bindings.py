from __future__ import annotations

from ui.window_appearance_state import (
    on_animations_changed,
    on_editor_smooth_scroll_changed,
    on_smooth_scroll_changed,
)
from settings.mode import ZAPRET1_MODE, ZAPRET2_MODE


def connect_window_page_signals(window) -> None:
    """Wire up page signals for MainWindow.

    Kept out of ui.main_window so the window class stays focused on
    composition/navigation instead of event wiring.
    """
    try:
        store = window.app_context.preset_store_winws2
        store.preset_switched.connect(window._preset_runtime_coordinator.handle_preset_switched)
        store.preset_identity_changed.connect(window._preset_runtime_coordinator.handle_preset_identity_changed)
        store.preset_content_changed.connect(
            lambda file_name, method=ZAPRET2_MODE: window._preset_runtime_coordinator.handle_preset_content_changed(
                method,
                file_name,
            )
        )
    except Exception:
        pass

    try:
        store_winws1 = window.app_context.preset_store_winws1
        store_winws1.preset_switched.connect(window._preset_runtime_coordinator.handle_preset_switched)
        store_winws1.preset_identity_changed.connect(window._preset_runtime_coordinator.handle_preset_identity_changed)
        store_winws1.preset_content_changed.connect(
            lambda file_name, method=ZAPRET1_MODE: window._preset_runtime_coordinator.handle_preset_content_changed(
                method,
                file_name,
            )
        )
    except Exception:
        pass

    try:
        window._preset_runtime_coordinator.setup_active_preset_file_watcher()
    except Exception:
        pass

    try:
        from settings.store import get_animations_enabled
        on_animations_changed(window, get_animations_enabled())
    except Exception:
        pass

    try:
        from settings.store import get_smooth_scroll_enabled
        on_smooth_scroll_changed(window, get_smooth_scroll_enabled())
    except Exception:
        pass

    try:
        from settings.store import get_editor_smooth_scroll_enabled

        on_editor_smooth_scroll_changed(window, get_editor_smooth_scroll_enabled())
    except Exception:
        pass


__all__ = ["connect_window_page_signals"]
