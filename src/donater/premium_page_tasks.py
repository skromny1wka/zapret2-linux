"""Фоновые задачи Premium page."""

from __future__ import annotations


def is_premium_task_running(thread) -> bool:
    """Проверяет, занят ли текущий Premium worker."""
    return bool(thread and thread.isRunning())


def stop_premium_worker_task(thread, *, wait_timeout_ms: int) -> None:
    """Мягко останавливает Premium worker thread и добивает его при зависании."""
    if not is_premium_task_running(thread):
        return
    thread.quit()
    thread.wait(wait_timeout_ms)
    if thread.isRunning():
        thread.terminate()
        thread.wait(500)
