from __future__ import annotations

import time

from app_notifications import advisory_notification, notification_action
from log.log import log

from winws_runtime.health.process_health_check import (
    check_conflicting_processes,
    get_conflicting_processes_report,
    try_kill_conflicting_processes,
)


def store_pending_conflict_request(controller, selected_mode=None, launch_method=None) -> int:
    controller._pending_conflict_request_id += 1
    controller._pending_conflict_selected_mode = selected_mode
    controller._pending_conflict_launch_method = launch_method
    return int(controller._pending_conflict_request_id)


def has_pending_conflict_request(controller, request_id: int) -> bool:
    return int(request_id or 0) == int(controller._pending_conflict_request_id or 0)


def clear_pending_conflict_request(controller, request_id: int | None = None) -> None:
    if request_id is not None and not has_pending_conflict_request(controller, int(request_id)):
        return
    controller._pending_conflict_selected_mode = None
    controller._pending_conflict_launch_method = None


def show_conflicting_processes_infobar(controller, conflicting: list[dict], request_id: int) -> None:
    names = ", ".join(str(item.get("name") or item.get("exe") or "неизвестно") for item in conflicting)
    controller.app.window_notification_controller.notify(
        advisory_notification(
            level="warning",
            title="Обнаружены конфликтующие программы",
            content=(
                "Обнаружены программы, которые блокируют WinDivert:\n\n"
                f"{names}\n\n"
                "Эти программы перехватывают системные вызовы и не дают "
                "WinDivert драйверу запуститься."
            ),
            source="launch.conflicting_processes",
            presentation="infobar",
            queue="immediate",
            duration=-1,
            dedupe_key=f"launch.conflicting_processes:{request_id}",
            dedupe_window_ms=0,
            buttons=[
                notification_action("launch_conflict_kill_start", "Закрыть и продолжить", value=request_id),
                notification_action("launch_conflict_ignore_start", "Продолжить без закрытия", value=request_id),
                notification_action("launch_conflict_cancel", "Отмена", value=request_id),
            ],
        )
    )


def show_conflict_kill_failed_infobar(controller, request_id: int) -> None:
    controller.app.window_notification_controller.notify(
        advisory_notification(
            level="warning",
            title="Не удалось закрыть процессы",
            content=(
                "Некоторые конфликтующие процессы не удалось закрыть.\n"
                "Запуск DPI может завершиться ошибкой."
            ),
            source="launch.conflicting_processes.kill_failed",
            presentation="infobar",
            queue="immediate",
            duration=-1,
            dedupe_key=f"launch.conflicting_processes.kill_failed:{request_id}",
            dedupe_window_ms=0,
            buttons=[
                notification_action("launch_conflict_ignore_start", "Продолжить запуск", value=request_id),
                notification_action("launch_conflict_cancel", "Отмена", value=request_id),
            ],
        )
    )


def handle_conflicting_processes_before_start(controller, selected_mode=None, launch_method=None) -> bool:
    conflicting = check_conflicting_processes()
    if not conflicting:
        return True

    report = get_conflicting_processes_report()
    log(report, "WARNING")
    request_id = store_pending_conflict_request(controller, selected_mode, launch_method)
    show_conflicting_processes_infobar(controller, conflicting, request_id)
    controller.app.set_status("⚠️ Обнаружены конфликтующие программы. Решите, как продолжить запуск.")
    return False


def resume_start_after_conflict_resolution(controller, request_id: int, *, close_conflicts: bool) -> None:
    if not has_pending_conflict_request(controller, request_id):
        log(f"Пропуск устаревшего действия по конфликтующим процессам: {request_id}", "DEBUG")
        return

    selected_mode = controller._pending_conflict_selected_mode
    launch_method = controller._pending_conflict_launch_method

    if close_conflicts:
        log("Пользователь выбрал закрыть конфликтующие процессы", "INFO")
        killed = try_kill_conflicting_processes(auto_kill=True)
        if killed:
            log("Конфликтующие процессы закрыты, ожидание 1с...", "INFO")
            time.sleep(1)
        else:
            log("Не удалось закрыть все конфликтующие процессы", "WARNING")
            show_conflict_kill_failed_infobar(controller, request_id)
            return
    else:
        log("Пользователь продолжил запуск несмотря на конфликтующие процессы", "WARNING")

    clear_pending_conflict_request(controller, request_id)
    controller.start_dpi_async(
        selected_mode=selected_mode,
        launch_method=launch_method,
        _skip_conflict_prompt=True,
    )


def cancel_start_after_conflict_prompt(controller, request_id: int) -> None:
    if not has_pending_conflict_request(controller, request_id):
        return
    clear_pending_conflict_request(controller, request_id)
    controller.app.set_status("Запуск DPI отменён пользователем")
    log("Запуск DPI отменён пользователем из-за конфликтующих процессов", "INFO")
