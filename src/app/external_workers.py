from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal

from log.log import log


class ExternalOpenUrlWorker(QThread):
    loaded = pyqtSignal(int, object)
    failed = pyqtSignal(int, str)

    def __init__(self, request_id: int, *, url: str, open_url, parent=None):
        super().__init__(parent)
        self._request_id = int(request_id)
        self._url = str(url or "").strip()
        self._open_url = open_url

    def run(self) -> None:
        try:
            result = self._open_url(self._url)
        except Exception as exc:
            log(f"ExternalOpenUrlWorker: не удалось открыть ссылку: {exc}", "ERROR")
            self.failed.emit(self._request_id, str(exc))
            return
        self.loaded.emit(self._request_id, result)


__all__ = ["ExternalOpenUrlWorker"]
