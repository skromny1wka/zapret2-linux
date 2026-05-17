from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class UpdateChannelActionResult:
    ok: bool
    message: str


def is_auto_update_enabled() -> bool:
    from settings.store import get_auto_update_enabled

    return bool(get_auto_update_enabled())


def set_auto_update_enabled(enabled: bool) -> None:
    from settings.store import set_auto_update_enabled

    set_auto_update_enabled(bool(enabled))


def run_startup_update_check() -> dict:
    from updater.startup_update_check import check_for_update_sync

    return check_for_update_sync()


def open_update_channel(channel: str) -> UpdateChannelActionResult:
    from config.telegram_links import open_telegram_link
    from updater.channel_utils import is_dev_update_channel

    try:
        domain = "zapretguidev" if is_dev_update_channel(channel) else "zapretnetdiscordyoutube"
        open_telegram_link(domain)
        return UpdateChannelActionResult(True, domain)
    except Exception as exc:
        return UpdateChannelActionResult(False, str(exc))
