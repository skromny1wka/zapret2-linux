from __future__ import annotations

from log.log import log


def start_telegram_proxy_if_enabled() -> None:
    """Запускает Telegram Proxy после основного запуска, если он включён."""
    try:
        from telegram_proxy.manager import start_proxy_if_enabled_async

        started = bool(start_proxy_if_enabled_async())
        if started:
            log("Telegram Proxy включён и запланирован после старта приложения", "INFO")
        else:
            log("Telegram Proxy выключен или уже запущен", "DEBUG")
    except Exception as exc:
        log(f"Ошибка запуска Telegram Proxy: {exc}", "WARNING")
