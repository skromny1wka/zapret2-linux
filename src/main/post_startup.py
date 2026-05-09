from __future__ import annotations

from typing import TYPE_CHECKING

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
from main.post_startup_tray import install_tray_startup
from main.post_startup_update import install_update_check

if TYPE_CHECKING:
    from main.window import LupiDPIApp


def install_post_startup_tasks(window: "LupiDPIApp") -> None:
    install_startup_checks(window)
    install_deferred_maintenance(window)
    install_telegram_proxy_startup(window)
    install_lists_check(window)
    install_dns_startup(window)
    install_tray_startup(window)
    install_update_check(window)
    install_cpu_diagnostic()
    install_qt_event_diagnostic_probe()
    install_global_exception_handler()
