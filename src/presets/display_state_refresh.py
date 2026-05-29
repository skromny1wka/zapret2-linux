from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from log.log import log
from settings.mode import is_preset_launch_method, normalize_launch_method


class PresetProfileStrategySummaryWorker(QThread):
    loaded = pyqtSignal(int, object)
    failed = pyqtSignal(int, str)

    def __init__(
        self,
        request_id: int,
        *,
        method: str,
        profile_feature,
        max_items: int = 2,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._request_id = int(request_id)
        self._method = normalize_launch_method(method, default="")
        self._profile_feature = profile_feature
        self._max_items = max(1, int(max_items))

    def run(self) -> None:
        try:
            from presets.display_state import resolve_profile_strategy_display_state

            result = resolve_profile_strategy_display_state(
                method=self._method,
                profile_feature=self._profile_feature,
                max_items=self._max_items,
            )
        except Exception as exc:
            log(f"PresetProfileStrategySummaryWorker: не удалось обновить summary profile: {exc}", "DEBUG")
            self.failed.emit(self._request_id, str(exc))
            return
        self.loaded.emit(self._request_id, result)


class PresetProfileStrategySummaryRefreshRuntime(QObject):
    """Запрашивает пересчёт краткого summary profile вне GUI-потока."""

    def __init__(
        self,
        *,
        profile_feature,
        state_store,
        get_launch_method: Callable[[], str],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._profile_feature = profile_feature
        self._state_store = state_store
        self._get_launch_method = get_launch_method
        self._request_id = 0
        self._worker: PresetProfileStrategySummaryWorker | None = None
        self._pending = False

    def request_refresh(self) -> None:
        method = normalize_launch_method(self._get_launch_method(), default="")
        if not method or not is_preset_launch_method(method):
            return

        worker = self._worker
        if worker is not None:
            try:
                if worker.isRunning():
                    self._pending = True
                    return
            except Exception:
                self._worker = None

        self._start_worker(method)

    def _start_worker(self, method: str) -> None:
        self._pending = False
        self._request_id += 1
        request_id = self._request_id
        worker = PresetProfileStrategySummaryWorker(
            request_id,
            method=method,
            profile_feature=self._profile_feature,
            parent=self,
        )
        self._worker = worker
        worker.loaded.connect(self._on_summary_loaded)
        worker.failed.connect(self._on_summary_failed)
        worker.finished.connect(lambda w=worker: self._on_worker_finished(w))
        worker.start()

    def _on_summary_loaded(self, request_id: int, state) -> None:
        if request_id != self._request_id:
            return
        from presets.display_state import publish_profile_strategy_summary_in_store

        publish_profile_strategy_summary_in_store(
            state=state,
            ui_state_store=self._state_store,
        )

    def _on_summary_failed(self, request_id: int, error: str) -> None:
        if request_id == self._request_id:
            log(f"Preset summary refresh skipped: {error}", "DEBUG")

    def _on_worker_finished(self, worker: PresetProfileStrategySummaryWorker) -> None:
        if self._worker is worker:
            self._worker = None
        worker.deleteLater()
        if self._pending:
            self.request_refresh()


__all__ = [
    "PresetProfileStrategySummaryRefreshRuntime",
    "PresetProfileStrategySummaryWorker",
]
