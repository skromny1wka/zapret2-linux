from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.page_names import PageName


@dataclass(frozen=True, slots=True)
class PageDepsContext:
    autostart_feature: object
    blobs_feature: object
    blockcheck_feature: object
    diagnostics_feature: object
    dns_feature: object
    dpi_settings_feature: object
    external_actions_feature: object
    hosts_feature: object
    lists_feature: object
    logs_feature: object
    orchestra_feature: object
    premium_feature: object
    presets_feature: object
    profile_feature: object
    program_settings_feature: object
    runtime_feature: object
    telegram_proxy_feature: object
    updater_feature: object
    ui_state_store: object
    set_status: Callable
    request_exit: Callable
    open_connection_test: Callable
    open_folder: Callable
    show_page: Callable
    show_active_mode_control_page: Callable
    open_profile_setup: Callable
    on_profile_setup_changed: Callable
    open_preset_raw_editor: Callable
    after_launch_method_changed: Callable
    set_garland_enabled: Callable
    set_snowflakes_enabled: Callable
    on_background_refresh_needed: Callable
    on_background_preset_changed: Callable
    on_opacity_changed: Callable
    on_mica_changed: Callable
    on_animations_changed: Callable
    on_smooth_scroll_changed: Callable
    on_editor_smooth_scroll_changed: Callable
    on_ui_language_changed: Callable


PageDepsBuilder = Callable[[PageDepsContext, PageName], dict]


__all__ = [
    "PageDepsContext",
    "PageDepsBuilder",
]
