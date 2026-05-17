from __future__ import annotations

from typing import Callable

from autostart.task_scheduler_api import (
    CANONICAL_TASK_NAME,
    delete_canonical_autostart_task,
)
from log.log import log


def clear_autostart_task(*, status_cb: Callable[[str], None] | None = None) -> int:
    """Удаляет только каноническую задачу автозапуска."""
    if status_cb is not None:
        try:
            status_cb("Удаление задачи автозапуска…")
        except Exception:
            pass

    log(f"Пробуем удалить задачу автозапуска {CANONICAL_TASK_NAME}", "INFO")
    if delete_canonical_autostart_task():
        log("Каноническая задача автозапуска удалена", "INFO")
        return 1

    log(f"Задача {CANONICAL_TASK_NAME} не найдена или уже удалена", "INFO")
    return 0
