from __future__ import annotations

from ui.page_deps.common import PageDepsContext
from ui.ui_root import WindowUiRoot
from ui.window_bootstrap_runtime import WindowRuntimeBootstrapDeps


def build_window_page_deps_context(*, features, state, page_actions) -> PageDepsContext:
    return PageDepsContext(
        autostart_feature=features.autostart,
        blobs_feature=features.blobs,
        blockcheck_feature=features.blockcheck,
        diagnostics_feature=features.diagnostics,
        dns_feature=features.dns,
        dpi_settings_feature=features.dpi_settings,
        external_actions_feature=features.external_actions,
        hosts_feature=features.hosts,
        lists_feature=features.lists,
        logs_feature=features.logs,
        orchestra_feature=features.orchestra,
        premium_feature=features.premium,
        presets_feature=features.presets,
        profile_feature=features.profile,
        program_settings_feature=features.program_settings,
        runtime_feature=features.runtime,
        telegram_proxy_feature=features.telegram_proxy,
        updater_feature=features.updater,
        ui_state_store=state.ui,
        set_status=page_actions.set_status,
        request_exit=page_actions.request_exit,
        open_connection_test=page_actions.open_connection_test,
        open_folder=page_actions.open_folder,
        show_page=page_actions.show_page,
        show_active_mode_control_page=page_actions.show_active_mode_control_page,
        open_profile_setup=page_actions.open_profile_setup,
        on_profile_setup_changed=page_actions.on_profile_setup_changed,
        open_preset_raw_editor=page_actions.open_preset_raw_editor,
        after_launch_method_changed=page_actions.after_launch_method_changed,
        set_garland_enabled=page_actions.set_garland_enabled,
        set_snowflakes_enabled=page_actions.set_snowflakes_enabled,
        on_background_refresh_needed=page_actions.on_background_refresh_needed,
        on_background_preset_changed=page_actions.on_background_preset_changed,
        on_opacity_changed=page_actions.on_opacity_changed,
        on_mica_changed=page_actions.on_mica_changed,
        on_animations_changed=page_actions.on_animations_changed,
        on_smooth_scroll_changed=page_actions.on_smooth_scroll_changed,
        on_editor_smooth_scroll_changed=page_actions.on_editor_smooth_scroll_changed,
        on_ui_language_changed=page_actions.on_ui_language_changed,
    )


def attach_window_ui_root(window, *, features, state, page_actions) -> None:
    runtime_bootstrap_deps = WindowRuntimeBootstrapDeps(
        runtime_feature=features.runtime,
        presets_feature=features.presets,
        profile_feature=features.profile,
        ui_state_store=state.ui,
        notify=page_actions.notify,
        set_status=page_actions.set_status,
    )
    window._ui_root = WindowUiRoot(
        window,
        build_window_page_deps_context(
            features=features,
            state=state,
            page_actions=page_actions,
        ),
        runtime_bootstrap_deps,
    )


__all__ = ["attach_window_ui_root", "build_window_page_deps_context"]
