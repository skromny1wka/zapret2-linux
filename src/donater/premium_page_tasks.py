"""Фоновые задачи Premium page."""

from __future__ import annotations


def is_premium_task_running(thread) -> bool:
    """Проверяет, занят ли текущий Premium worker."""
    return bool(thread and thread.isRunning())


def start_premium_worker_task(
    *,
    premium_feature,
    task_callable,
    result_handler,
    error_handler,
    finished_handler,
):
    """Создаёт, подключает и запускает Premium worker thread."""
    thread = premium_feature.create_premium_worker_thread(task_callable)
    thread.result_ready.connect(result_handler)
    thread.error_occurred.connect(error_handler)
    thread.finished.connect(finished_handler)
    thread.finished.connect(thread.deleteLater)
    thread.start()
    return thread


def stop_premium_worker_task(thread, *, wait_timeout_ms: int) -> None:
    """Мягко останавливает Premium worker thread и добивает его при зависании."""
    if not is_premium_task_running(thread):
        return
    thread.quit()
    thread.wait(wait_timeout_ms)
    if thread.isRunning():
        thread.terminate()
        thread.wait(500)
