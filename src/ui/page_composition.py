from __future__ import annotations

from app.page_names import PageName
from ui.page_deps.common import PageDepsBuilder
from ui.page_deps.presets import (
    build_control_page_kwargs,
    build_preset_raw_editor_page_kwargs,
    build_preset_setup_page_kwargs,
    build_profile_setup_page_kwargs,
    build_user_presets_page_kwargs,
)
from ui.page_deps.system import (
    build_about_page_kwargs,
    build_appearance_page_kwargs,
    build_autostart_page_kwargs,
    build_blobs_page_kwargs,
    build_blockcheck_page_kwargs,
    build_dpi_settings_page_kwargs,
    build_hosts_page_kwargs,
    build_lists_page_kwargs,
    build_logs_page_kwargs,
    build_network_page_kwargs,
    build_orchestra_page_kwargs,
    build_orchestra_settings_page_kwargs,
    build_premium_page_kwargs,
    build_servers_page_kwargs,
    build_support_page_kwargs,
    build_telegram_proxy_page_kwargs,
)
from ui.page_deps.types import DnsPageDeps, HostsPageDeps, PremiumPageDeps


PAGE_DEPS_BUILDERS: dict[PageName, PageDepsBuilder] = {
    PageName.ZAPRET2_MODE_CONTROL: build_control_page_kwargs,
    PageName.ZAPRET1_MODE_CONTROL: build_control_page_kwargs,
    PageName.ZAPRET2_PRESET_SETUP: build_preset_setup_page_kwargs,
    PageName.ZAPRET1_PRESET_SETUP: build_preset_setup_page_kwargs,
    PageName.ZAPRET2_PROFILE_SETUP: build_profile_setup_page_kwargs,
    PageName.ZAPRET1_PROFILE_SETUP: build_profile_setup_page_kwargs,
    PageName.ZAPRET2_USER_PRESETS: build_user_presets_page_kwargs,
    PageName.ZAPRET1_USER_PRESETS: build_user_presets_page_kwargs,
    PageName.ZAPRET2_PRESET_RAW_EDITOR: build_preset_raw_editor_page_kwargs,
    PageName.ZAPRET1_PRESET_RAW_EDITOR: build_preset_raw_editor_page_kwargs,
    PageName.DPI_SETTINGS: build_dpi_settings_page_kwargs,
    PageName.BLOBS: build_blobs_page_kwargs,
    PageName.HOSTLIST: build_lists_page_kwargs,
    PageName.NETROGAT: build_lists_page_kwargs,
    PageName.CUSTOM_DOMAINS: build_lists_page_kwargs,
    PageName.CUSTOM_IPSET: build_lists_page_kwargs,
    PageName.NETWORK: build_network_page_kwargs,
    PageName.HOSTS: build_hosts_page_kwargs,
    PageName.PREMIUM: build_premium_page_kwargs,
    PageName.SUPPORT: build_support_page_kwargs,
    PageName.AUTOSTART: build_autostart_page_kwargs,
    PageName.APPEARANCE: build_appearance_page_kwargs,
    PageName.ABOUT: build_about_page_kwargs,
    PageName.SERVERS: build_servers_page_kwargs,
    PageName.BLOCKCHECK: build_blockcheck_page_kwargs,
    PageName.LOGS: build_logs_page_kwargs,
    PageName.TELEGRAM_PROXY: build_telegram_proxy_page_kwargs,
    PageName.ORCHESTRA: build_orchestra_page_kwargs,
    PageName.ORCHESTRA_SETTINGS: build_orchestra_settings_page_kwargs,
}


def validate_page_deps_builder_coverage(page_names) -> None:
    missing = tuple(page_name for page_name in page_names if page_name not in PAGE_DEPS_BUILDERS)
    if missing:
        names = ", ".join(page_name.name for page_name in missing)
        raise RuntimeError(f"Missing page deps builders: {names}")


def build_page_deps(context, page_name: PageName) -> dict:
    """Возвращает зависимости страницы по явной карте."""
    builder = PAGE_DEPS_BUILDERS.get(page_name)
    if builder is None:
        raise RuntimeError(f"Missing page deps builder for {page_name.name}")
    return builder(context, page_name)


__all__ = [
    "DnsPageDeps",
    "HostsPageDeps",
    "PAGE_DEPS_BUILDERS",
    "PremiumPageDeps",
    "build_page_deps",
    "validate_page_deps_builder_coverage",
]
