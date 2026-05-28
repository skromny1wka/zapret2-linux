from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal

from log.log import log


class WindowGeometrySaveWorker(QThread):
    saved = pyqtSignal(object, object)
    failed = pyqtSignal(str)

    def __init__(
        self,
        *,
        geometry: tuple[int, int, int, int] | None,
        maximized: bool,
        parent=None,
    ):
        super().__init__(parent)
        self._geometry = None if geometry is None else tuple(int(value) for value in geometry)
        self._maximized = bool(maximized)

    def run(self) -> None:
        try:
            from settings import store as settings_store

            if self._geometry is None:
                current = settings_store.get_window_geometry()
                x = current.get("x")
                y = current.get("y")
                width = current.get("width")
                height = current.get("height")
            else:
                x, y, width, height = self._geometry

            settings_store.set_window_geometry(
                x=x,
                y=y,
                width=width,
                height=height,
                maximized=self._maximized,
            )
        except Exception as exc:
            log(f"WindowGeometrySaveWorker: не удалось сохранить геометрию: {exc}", "WARNING")
            self.failed.emit(str(exc))
            return
        self.saved.emit(self._geometry, self._maximized)


__all__ = ["WindowGeometrySaveWorker"]
