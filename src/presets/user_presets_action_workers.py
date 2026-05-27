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


class UserPresetItemActionWorker(QThread):
    completed = pyqtSignal(int, str, object, object)
    failed = pyqtSignal(int, str, str)

    def __init__(
        self,
        request_id: int,
        actions_api,
        *,
        action: str,
        file_name: str,
        display_name: str,
        file_path: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self._request_id = int(request_id)
        self.actions_api = actions_api
        self._action = str(action or "").strip()
        self._file_name = str(file_name or "").strip()
        self._display_name = str(display_name or self._file_name).strip()
        self._file_path = str(file_path or "").strip()

    def run(self) -> None:
        try:
            if self._action == "duplicate":
                result = self.actions_api.duplicate_preset(
                    file_name=self._file_name,
                    display_name=self._display_name,
                )
            elif self._action == "reset":
                result = self.actions_api.reset_preset_to_builtin(
                    file_name=self._file_name,
                    display_name=self._display_name,
                )
            elif self._action == "delete":
                result = self.actions_api.delete_preset(
                    file_name=self._file_name,
                    display_name=self._display_name,
                )
            elif self._action == "export":
                result = self.actions_api.export_preset(
                    file_name=self._file_name,
                    file_path=self._file_path,
                    display_name=self._display_name,
                )
            else:
                raise ValueError(f"Неизвестное действие preset: {self._action}")
        except Exception as exc:
            log(f"UserPresetItemActionWorker: действие {self._action} не выполнено: {exc}", "ERROR")
            self.failed.emit(self._request_id, self._action, str(exc))
            return
        context = {
            "file_name": self._file_name,
            "display_name": self._display_name,
            "file_path": self._file_path,
        }
        self.completed.emit(self._request_id, self._action, result, context)


__all__ = ["UserPresetActivateWorker", "UserPresetItemActionWorker"]
