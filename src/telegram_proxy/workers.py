from __future__ import annotations

import time

from PyQt6.QtCore import QThread, pyqtSignal

from log.log import log


class TelegramProxyStartWorker(QThread):
    completed = pyqtSignal(bool)

    def __init__(self, *, manager, port: int, mode: str, host: str, upstream_config, parent=None):
        super().__init__(parent)
        self._manager = manager
        self._port = int(port)
        self._mode = str(mode or "socks5")
        self._host = str(host or "127.0.0.1")
        self._upstream_config = upstream_config

    def run(self) -> None:
        try:
            ok = self._manager.start_proxy(
                port=self._port,
                mode=self._mode,
                host=self._host,
                upstream_config=self._upstream_config,
            )
        except Exception as exc:
            log(f"TelegramProxyStartWorker: ошибка запуска proxy: {exc}", "WARNING")
            ok = False
        self.completed.emit(bool(ok))


class TelegramProxyStopRuntimeWorker(QThread):
    stopped = pyqtSignal()

    def __init__(self, *, manager, parent=None):
        super().__init__(parent)
        self._manager = manager

    def run(self) -> None:
        try:
            self._manager._stop_runtime_only()
        except Exception as exc:
            log(f"TelegramProxyStopRuntimeWorker: ошибка остановки proxy: {exc}", "WARNING")
        self.stopped.emit()


class TelegramProxyRelayCheckWorker(QThread):
    completed = pyqtSignal(int, dict)
    warning = pyqtSignal(str)

    def __init__(self, *, generation: int, get_zapret_running, parent=None):
        super().__init__(parent)
        self._generation = int(generation)
        self._get_zapret_running = get_zapret_running

    def run(self) -> None:
        try:
            from telegram_proxy.wss_proxy import check_relay_reachable
            import telegram_proxy.ui.page_runtime as telegram_proxy_page_runtime

            time.sleep(2)
            best_result = None
            for attempt in range(3):
                result = check_relay_reachable(timeout=5.0)
                if result["reachable"]:
                    best_result = result
                    break
                if attempt < 2:
                    time.sleep(2)

            if best_result and best_result["reachable"]:
                diag = {"status": "ok", "ms": best_result["ms"]}
            else:
                diag = {
                    "status": "fail",
                    "http_ok": telegram_proxy_page_runtime.check_relay_http(),
                    "zapret_running": bool(self._get_zapret_running()),
                }
            self.completed.emit(self._generation, diag)
        except Exception as exc:
            self.warning.emit(f"Relay check error: {exc}")


class TelegramProxyDiagnosticsWorker(QThread):
    progress = pyqtSignal(str)
    completed = pyqtSignal(str)

    def __init__(self, *, run_diagnostics_fn, proxy_port: int, parent=None):
        super().__init__(parent)
        self._run_diagnostics_fn = run_diagnostics_fn
        self._proxy_port = int(proxy_port)

    def run(self) -> None:
        try:
            result_text = self._run_diagnostics_fn(
                proxy_port=self._proxy_port,
                progress_callback=self.progress.emit,
            )
        except Exception as exc:
            log(f"TelegramProxyDiagnosticsWorker: ошибка диагностики: {exc}", "WARNING")
            result_text = str(exc)
        self.completed.emit(str(result_text or ""))


class TelegramHostsEnsureWorker(QThread):
    completed = pyqtSignal(object)

    def __init__(self, *, ensure_hosts_fn, parent=None):
        super().__init__(parent)
        self._ensure_hosts_fn = ensure_hosts_fn

    def run(self) -> None:
        try:
            plan = self._ensure_hosts_fn()
        except Exception as exc:
            log(f"TelegramHostsEnsureWorker: ошибка проверки hosts: {exc}", "WARNING")
            plan = None
        self.completed.emit(plan)
