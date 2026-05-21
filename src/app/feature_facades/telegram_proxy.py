from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True, slots=True)
class TelegramProxyFeature:
    start_proxy_if_enabled_async: Callable
    get_proxy_manager: Callable
    get_start_config: Callable
    set_enabled: Callable
    build_diagnostics_start_plan: Callable
    build_diagnostics_poll_plan: Callable
    build_diagnostics_finish_plan: Callable
    copy_text: Callable
    open_log_file: Callable
    open_external_link: Callable
    ensure_telegram_hosts: Callable
    run_diagnostics: Callable

    def is_running(self) -> bool:
        try:
            return bool(self.get_proxy_manager().is_running)
        except Exception:
            return False

    def status_label(self) -> str:
        try:
            manager = self.get_proxy_manager()
            if manager.is_running:
                return f"Telegram Proxy: вкл ({manager.port})"
        except Exception:
            pass
        return "Telegram Proxy: выкл"

    def connect_status_changed(self, callback) -> None:
        try:
            self.get_proxy_manager().status_changed.connect(callback)
        except Exception:
            pass

    def cleanup(self) -> None:
        try:
            self.get_proxy_manager().cleanup()
        except Exception:
            pass

    def create_start_worker(self, *, manager, port: int, mode: str, host: str, upstream_config, parent=None):
        from telegram_proxy.workers import TelegramProxyStartWorker

        return TelegramProxyStartWorker(
            manager=manager,
            port=port,
            mode=mode,
            host=host,
            upstream_config=upstream_config,
            parent=parent,
        )

    def create_stop_runtime_worker(self, *, manager, parent=None):
        from telegram_proxy.workers import TelegramProxyStopRuntimeWorker

        return TelegramProxyStopRuntimeWorker(manager=manager, parent=parent)

    def create_relay_check_worker(self, *, generation: int, get_zapret_running, parent=None):
        from telegram_proxy.workers import TelegramProxyRelayCheckWorker

        return TelegramProxyRelayCheckWorker(
            generation=generation,
            get_zapret_running=get_zapret_running,
            parent=parent,
        )

    def create_diagnostics_worker(self, *, proxy_port: int, parent=None):
        from telegram_proxy.workers import TelegramProxyDiagnosticsWorker

        return TelegramProxyDiagnosticsWorker(
            run_diagnostics_fn=self.run_diagnostics,
            proxy_port=proxy_port,
            parent=parent,
        )

    def create_ensure_hosts_worker(self, *, parent=None):
        from telegram_proxy.workers import TelegramHostsEnsureWorker

        return TelegramHostsEnsureWorker(ensure_hosts_fn=self.ensure_telegram_hosts, parent=parent)

    def toggle_async(self) -> None:
        try:
            manager = self.get_proxy_manager()
            if manager.is_running:
                manager.stop_proxy()
                self.set_enabled(False)
                return

            config = self.get_start_config()
            worker = self.create_start_worker(
                manager=manager,
                port=config.port,
                mode=config.mode,
                host=config.host,
                upstream_config=config.upstream_config,
            )
            setattr(manager, "_tray_start_worker", worker)
            worker.finished.connect(lambda: setattr(manager, "_tray_start_worker", None))
            worker.finished.connect(worker.deleteLater)
            worker.start()
        except Exception as exc:
            from log.log import log

            log(f"Telegram Proxy toggle error: {exc}", "WARNING")


def build_telegram_proxy_feature() -> TelegramProxyFeature:
    from telegram_proxy import commands as telegram_proxy_commands
    from telegram_proxy import public as telegram_proxy_public

    return TelegramProxyFeature(
        start_proxy_if_enabled_async=telegram_proxy_public.start_proxy_if_enabled_async,
        get_proxy_manager=telegram_proxy_commands.get_proxy_manager,
        get_start_config=telegram_proxy_commands.get_start_config,
        set_enabled=telegram_proxy_public.set_enabled,
        build_diagnostics_start_plan=telegram_proxy_public.build_diagnostics_start_plan,
        build_diagnostics_poll_plan=telegram_proxy_public.build_diagnostics_poll_plan,
        build_diagnostics_finish_plan=telegram_proxy_public.build_diagnostics_finish_plan,
        copy_text=telegram_proxy_public.copy_text,
        open_log_file=telegram_proxy_public.open_log_file,
        open_external_link=telegram_proxy_public.open_external_link,
        ensure_telegram_hosts=telegram_proxy_public.ensure_telegram_hosts,
        run_diagnostics=telegram_proxy_public.run_diagnostics,
    )
