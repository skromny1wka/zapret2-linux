from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal

from log.log import log
from utils.subproc import run_hidden


class WindowOpenFolderWorker(QThread):
    completed = pyqtSignal()
    failed = pyqtSignal(str)

    def run(self) -> None:
        try:
            run_hidden("explorer.exe .", shell=True)
        except Exception as exc:
            log(f"WindowOpenFolderWorker: не удалось открыть папку программы: {exc}", "ERROR")
            self.failed.emit(str(exc))
            return
        self.completed.emit()


__all__ = ["WindowOpenFolderWorker"]
