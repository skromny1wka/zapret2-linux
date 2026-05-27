from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal

from log.log import log


class UserPresetActivateWorker(QThread):
    activated = pyqtSignal(int, object)
    failed = pyqtSignal(int, str)

    def __init__(self, request_id: int, actions_api, *, file_name: str, display_name: str, parent=None):
        super().__init__(parent)
        self._request_id = int(request_id)
        self.actions_api = actions_api
        self._file_name = str(file_name or "").strip()
        self._display_name = str(display_name or self._file_name).strip()

    def run(self) -> None:
        try:
            result = self.actions_api.activate_preset(
                file_name=self._file_name,
                display_name=self._display_name,
            )
        except Exception as exc:
            log(f"UserPresetActivateWorker: не удалось активировать preset: {exc}", "ERROR")
            self.failed.emit(self._request_id, str(exc))
            return
        self.activated.emit(self._request_id, result)


__all__ = ["UserPresetActivateWorker"]
