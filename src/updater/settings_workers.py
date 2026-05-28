from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal

from log.log import log


class UpdaterAutoCheckSaveWorker(QThread):
    loaded = pyqtSignal(int, bool)
    failed = pyqtSignal(int, str)

    def __init__(self, request_id: int, updater_feature, *, enabled: bool, parent=None):
        super().__init__(parent)
        self._request_id = int(request_id)
        self._updater = updater_feature
        self._enabled = bool(enabled)

    def run(self) -> None:
        try:
            self._updater.set_auto_update_enabled(self._enabled)
        except Exception as exc:
            log(f"UpdaterAutoCheckSaveWorker: настройка автопроверки не сохранена: {exc}", "ERROR")
            self.failed.emit(self._request_id, str(exc))
            return
        self.loaded.emit(self._request_id, self._enabled)
