from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal

from log.log import log


class DnsPageLoadWorker(QThread):
    loaded = pyqtSignal(object)
    finished_loading = pyqtSignal()

    def __init__(self, load_page_data_fn, parent=None):
        super().__init__(parent)
        self._load_page_data_fn = load_page_data_fn

    def run(self) -> None:
        try:
            state = self._load_page_data_fn()
            self.loaded.emit(state)
        except Exception as exc:
            log(f"DnsPageLoadWorker: ошибка загрузки DNS страницы: {exc}", "ERROR")
        self.finished_loading.emit()


class DnsConnectivityTestWorker(QThread):
    completed = pyqtSignal(list)

    def __init__(self, run_connectivity_test_fn, test_hosts, parent=None):
        super().__init__(parent)
        self._run_connectivity_test_fn = run_connectivity_test_fn
        self._test_hosts = tuple(test_hosts or ())

    def run(self) -> None:
        try:
            results = self._run_connectivity_test_fn(self._test_hosts)
        except Exception as exc:
            log(f"DnsConnectivityTestWorker: ошибка проверки DNS: {exc}", "ERROR")
            results = []
        self.completed.emit(list(results or []))
