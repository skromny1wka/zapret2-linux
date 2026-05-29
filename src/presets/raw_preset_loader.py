from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal

from log.log import log


class RawPresetLoadWorker(QThread):
    loaded = pyqtSignal(int, object)
    failed = pyqtSignal(int, str)

    def __init__(self, request_id: int, load_preset, file_name: str, parent=None):
        super().__init__(parent)
        self._request_id = int(request_id)
        self._load_preset = load_preset
        self._file_name = str(file_name or "").strip()

    def run(self) -> None:
        try:
            result = self._load_preset(self._file_name)
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
        save_text,
        *,
        file_name: str,
        source_text: str,
        publish_content_changed: bool,
        parent=None,
    ):
        super().__init__(parent)
        self._request_id = int(request_id)
        self._save_text = save_text
        self._file_name = str(file_name or "").strip()
        self._source_text = str(source_text or "")
        self._publish_content_changed = bool(publish_content_changed)

    def run(self) -> None:
        try:
            result = self._save_text(
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


class RawPresetActionWorker(QThread):
    completed = pyqtSignal(int, str, object, object)
    failed = pyqtSignal(int, str, str, object)

    def __init__(
        self,
        request_id: int,
        run_action,
        *,
        action: str,
        payload: dict | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self._request_id = int(request_id)
        self._run_action = run_action
        self._action = str(action or "").strip()
        self._payload = dict(payload or {})

    def run(self) -> None:
        action = self._action
        payload = self._payload
        try:
            result = self._run_action(action, payload)
        except Exception as exc:
            log(f"RawPresetActionWorker: действие {action} не выполнено: {exc}", "ERROR")
            self.failed.emit(self._request_id, action, str(exc), payload)
            return
        self.completed.emit(self._request_id, action, result, payload)


class RawPresetActivateWorker(QThread):
    activated = pyqtSignal(int, bool)
    failed = pyqtSignal(int, str)

    def __init__(self, request_id: int, activate, file_name: str, parent=None):
        super().__init__(parent)
        self._request_id = int(request_id)
        self._activate = activate
        self._file_name = str(file_name or "").strip()

    def run(self) -> None:
        try:
            activated = bool(self._activate(file_name=self._file_name))
        except Exception as exc:
            log(f"RawPresetActivateWorker: не удалось активировать preset: {exc}", "ERROR")
            self.failed.emit(self._request_id, str(exc))
            return
        self.activated.emit(self._request_id, activated)
