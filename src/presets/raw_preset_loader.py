from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from log.log import log


class RawPresetLoadWorker(QThread):
    loaded = pyqtSignal(int, object)
    failed = pyqtSignal(int, str)

    def __init__(self, request_id: int, controller, path: Path | None, parent=None):
        super().__init__(parent)
        self._request_id = int(request_id)
        self._controller = controller
        self._path = path

    def run(self) -> None:
        try:
            result = self._controller.load_text(self._path)
        except Exception as exc:
            log(f"RawPresetLoadWorker: не удалось прочитать preset: {exc}", "ERROR")
            self.failed.emit(self._request_id, str(exc))
            return
        self.loaded.emit(self._request_id, result)


class RawPresetSaveWorker(QThread):
    saved = pyqtSignal(int, str, object, bool)
    failed = pyqtSignal(int, str)

    def __init__(
        self,
        request_id: int,
        controller,
        *,
        file_name: str,
        source_text: str,
        publish_content_changed: bool,
        parent=None,
    ):
        super().__init__(parent)
        self._request_id = int(request_id)
        self.controller = controller
        self._file_name = str(file_name or "").strip()
        self._source_text = str(source_text or "")
        self._publish_content_changed = bool(publish_content_changed)

    def run(self) -> None:
        try:
            result = self.controller.save_text(
                file_name=self._file_name,
                source_text=self._source_text,
                publish_content_changed=self._publish_content_changed,
            )
        except Exception as exc:
            log(f"RawPresetSaveWorker: не удалось сохранить preset: {exc}", "ERROR")
            self.failed.emit(self._request_id, str(exc))
            return
        self.saved.emit(
            self._request_id,
            self._file_name,
            result,
            self._publish_content_changed,
        )


class RawPresetActivateWorker(QThread):
    activated = pyqtSignal(int, bool)
    failed = pyqtSignal(int, str)

    def __init__(self, request_id: int, controller, file_name: str, parent=None):
        super().__init__(parent)
        self._request_id = int(request_id)
        self.controller = controller
        self._file_name = str(file_name or "").strip()

    def run(self) -> None:
        try:
            activated = bool(self.controller.activate(file_name=self._file_name))
        except Exception as exc:
            log(f"RawPresetActivateWorker: не удалось активировать preset: {exc}", "ERROR")
            self.failed.emit(self._request_id, str(exc))
            return
        self.activated.emit(self._request_id, activated)
