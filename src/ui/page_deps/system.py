from __future__ import annotations

from app.page_names import PageName
from ui.page_deps.common import PageDepsContext
from ui.page_deps.types import DnsPageDeps, HostsPageDeps, PremiumPageDeps


def build_dpi_settings_page_kwargs(context: PageDepsContext, _page_name: PageName) -> dict:
    return {
        "dpi_settings_feature": context.dpi_settings_feature,
        "orchestra_feature": context.orchestra_feature,
        "runtime_feature": context.runtime_feature,
        "set_status": context.set_status,
        "after_launch_method_changed": context.after_launch_method_changed,
    }


def build_blobs_page_kwargs(context: PageDepsContext, _page_name: PageName) -> dict:
    return {
        "blobs_feature": context.blobs_feature,
        "open_control": lambda: context.show_active_mode_control_page(allow_internal=False),
    }


def build_lists_page_kwargs(context: PageDepsContext, _page_name: PageName) -> dict:
    return {
        "lists_feature": context.lists_feature,
    }


def build_network_page_kwargs(context: PageDepsContext, _page_name: PageName) -> dict:
    return {
        "deps": DnsPageDeps(dns_feature=context.dns_feature),
    }


def build_hosts_page_kwargs(context: PageDepsContext, _page_name: PageName) -> dict:
    return {
        "deps": HostsPageDeps(hosts_feature=context.hosts_feature),
    }


def build_premium_page_kwargs(context: PageDepsContext, _page_name: PageName) -> dict:
    return {
        "deps": PremiumPageDeps(
            premium_feature=context.premium_feature,
            subscription_state_store=context.ui_state_store,
        ),
    }


def build_support_page_kwargs(_context: PageDepsContext, _page_name: PageName) -> dict:
    import about.plans as about_page_plans

    return {
        "open_discussions": about_page_plans.open_support_discussions,
        "open_telegram": lambda: about_page_plans.open_telegram("zaprethelp"),
        "open_discord": lambda: about_page_plans.open_discord("https://discord.gg/kkcBDG2uws"),
    }


def build_autostart_page_kwargs(context: PageDepsContext, _page_name: PageName) -> dict:
    return {
        "autostart_feature": context.autostart_feature,
        "open_dpi_settings": lambda: context.show_page(PageName.DPI_SETTINGS),
        "ui_state_store": context.ui_state_store,
    }


def build_appearance_page_kwargs(context: PageDepsContext, _page_name: PageName) -> dict:
    return {
        "on_garland_changed": context.set_garland_enabled,
        "on_snowflakes_changed": context.set_snowflakes_enabled,
        "on_background_refresh_needed": context.on_background_refresh_needed,
        "on_background_preset_changed": context.on_background_preset_changed,
        "on_opacity_changed": context.on_opacity_changed,
        "on_mica_changed": context.on_mica_changed,
        "on_animations_changed": context.on_animations_changed,
        "on_smooth_scroll_changed": context.on_smooth_scroll_changed,
        "on_editor_smooth_scroll_changed": context.on_editor_smooth_scroll_changed,
        "on_ui_language_changed": context.on_ui_language_changed,
        "ui_state_store": context.ui_state_store,
    }


def build_about_page_kwargs(context: PageDepsContext, _page_name: PageName) -> dict:
    import about.plans as about_page_plans

    return {
        "open_premium": lambda: context.show_page(PageName.PREMIUM),
        "open_updates": lambda: context.show_page(PageName.SERVERS, allow_internal=True),
        "open_discussions": about_page_plans.open_support_discussions,
        "open_support_telegram": lambda: about_page_plans.open_telegram("zaprethelp"),
        "open_support_discord": lambda: about_page_plans.open_discord("https://discord.gg/kkcBDG2uws"),
        "open_forum_for_beginners": lambda: about_page_plans.open_telegram("bypassblock", post=1359),
        "open_help_folder": about_page_plans.open_help_folder,
        "open_telegram_news": lambda: about_page_plans.open_telegram("bypassblock"),
        "open_kvn_channel": lambda: about_page_plans.open_telegram("vpndiscordyooutube"),
        "open_kvn_bot": lambda: about_page_plans.open_telegram("zapretvpns_bot"),
        "open_kvn_bypass": lambda: about_page_plans.open_telegram("bypassblock"),
        "open_kvn_github": lambda: about_page_plans.open_github("https://github.com/youtubediscord/zapret-kvn"),
        "ui_state_store": context.ui_state_store,
    }


def build_servers_page_kwargs(context: PageDepsContext, _page_name: PageName) -> dict:
    return {
        "runtime_feature": context.runtime_feature,
        "updater_feature": context.updater_feature,
        "open_about": lambda: context.show_page(PageName.ABOUT),
        "external_actions_feature": context.external_actions_feature,
    }


def build_blockcheck_page_kwargs(context: PageDepsContext, _page_name: PageName) -> dict:
    return {
        "blockcheck_feature": context.blockcheck_feature,
        "diagnostics_feature": context.diagnostics_feature,
        "dns_feature": context.dns_feature,
        "runtime_feature": context.runtime_feature,
    }


def build_logs_page_kwargs(context: PageDepsContext, _page_name: PageName) -> dict:
    return {
        "logs_feature": context.logs_feature,
        "orchestra_feature": context.orchestra_feature,
        "runtime_feature": context.runtime_feature,
    }


def build_telegram_proxy_page_kwargs(context: PageDepsContext, _page_name: PageName) -> dict:
    return {
        "runtime_feature": context.runtime_feature,
        "telegram_proxy_feature": context.telegram_proxy_feature,
    }


def build_orchestra_page_kwargs(context: PageDepsContext, _page_name: PageName) -> dict:
    from orchestra.page_controller import OrchestraPageController

    return {
        "controller": OrchestraPageController(
            orchestra_feature=context.orchestra_feature,
            runtime_feature=context.runtime_feature,
        ),
    }


def build_orchestra_settings_page_kwargs(context: PageDepsContext, _page_name: PageName) -> dict:
    from orchestra.managed_lists_controller import (
        BlockedStrategiesController,
        LockedStrategiesController,
        WhitelistController,
    )
    from orchestra.ratings_controller import OrchestraRatingsController

    return {
        "controllers": {
            "locked": LockedStrategiesController(context.orchestra_feature),
            "blocked": BlockedStrategiesController(context.orchestra_feature),
            "whitelist": WhitelistController(context.orchestra_feature),
            "ratings": OrchestraRatingsController(context.orchestra_feature),
        },
    }


__all__ = [
    "build_about_page_kwargs",
    "build_appearance_page_kwargs",
    "build_autostart_page_kwargs",
    "build_blockcheck_page_kwargs",
    "build_blobs_page_kwargs",
    "build_dpi_settings_page_kwargs",
    "build_hosts_page_kwargs",
    "build_lists_page_kwargs",
    "build_logs_page_kwargs",
    "build_network_page_kwargs",
    "build_orchestra_page_kwargs",
    "build_orchestra_settings_page_kwargs",
    "build_premium_page_kwargs",
    "build_servers_page_kwargs",
    "build_support_page_kwargs",
    "build_telegram_proxy_page_kwargs",
]
