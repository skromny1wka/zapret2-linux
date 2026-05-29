from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal

from log.log import log


class PremiumDeviceInfoLoadWorker(QThread):
    loaded = pyqtSignal(int, object)
    failed = pyqtSignal(int, str)

    def __init__(
        self,
        request_id: int,
        *,
        read_device_info_snapshot,
        current_time: int,
        parent=None,
    ):
        super().__init__(parent)
        self._request_id = int(request_id)
        self._read_device_info_snapshot = read_device_info_snapshot
        self._current_time = int(current_time)

    def run(self) -> None:
        try:
            snapshot = self._read_device_info_snapshot(current_time=self._current_time)
        except Exception as exc:
            log(f"PremiumDeviceInfoLoadWorker: не удалось загрузить данные устройства: {exc}", "DEBUG")
            self.failed.emit(self._request_id, str(exc))
            return
        self.loaded.emit(self._request_id, snapshot)


__all__ = ["PremiumDeviceInfoLoadWorker"]
