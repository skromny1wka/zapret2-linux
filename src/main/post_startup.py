from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from main.post_startup_checks import install_startup_checks
from main.post_startup_diagnostics import (
    install_cpu_diagnostic,
    install_global_exception_handler,
    install_qt_event_diagnostic_probe,
)
from main.post_startup_dns import install_dns_startup
from main.post_startup_lists import install_lists_check
from main.post_startup_maintenance import install_deferred_maintenance
from main.post_startup_proxy import install_telegram_proxy_startup
from main.post_startup_update import install_update_check

@dataclass(frozen=True, slots=True)
class PostStartupDeps:
    startup_host: Any
    notify: Any
    notify_many: Any
    set_status: Any
    log_startup_metric: Any
    start_proxy_if_enabled_async: Any
    startup_lists_check: Any
    apply_dns_on_startup_async: Any
    install_tray_post_startup: Any
    updater_feature: Any


def install_post_startup_tasks(deps: PostStartupDeps) -> None:
    startup_host = deps.startup_host

    install_startup_checks(
        startup_host,
        notify_many=deps.notify_many,
        set_status=deps.set_status,
        log_startup_metric=deps.log_startup_metric,
    )
    install_deferred_maintenance(
        startup_host,
        notify_many=deps.notify_many,
        log_startup_metric=deps.log_startup_metric,
    )
    install_telegram_proxy_startup(
        startup_host,
        start_proxy_if_enabled_async=deps.start_proxy_if_enabled_async,
        log_startup_metric=deps.log_startup_metric,
    )
    install_lists_check(
        startup_host,
        startup_lists_check=deps.startup_lists_check,
        log_startup_metric=deps.log_startup_metric,
    )
    install_dns_startup(
        startup_host,
        apply_dns_on_startup_async=deps.apply_dns_on_startup_async,
        set_status=deps.set_status,
        log_startup_metric=deps.log_startup_metric,
    )
    deps.install_tray_post_startup()
    install_update_check(
        startup_host,
        updater_feature=deps.updater_feature,
        notify=deps.notify,
        set_status=deps.set_status,
    )
    install_cpu_diagnostic()
    install_qt_event_diagnostic_probe()
    install_global_exception_handler()


__all__ = ["PostStartupDeps", "install_post_startup_tasks"]
