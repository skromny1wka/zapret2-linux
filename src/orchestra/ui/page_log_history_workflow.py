"""Workflow истории логов Orchestra page."""

from collections.abc import Callable

import orchestra.log_history_workflow as orchestra_log_history_workflow


def view_log_history_entry(
    *,
    runner,
    current_item,
    user_role,
    log_text,
    append_log: Callable[[str], None],
    log_debug: Callable[[str], None],
) -> None:
    """Открывает выбранный лог из истории."""
    if runner is None or current_item is None:
        return

    log_id = current_item.data(user_role)
    if not log_id:
        return

    try:
        result = orchestra_log_history_workflow.view_log_history_entry(
            runner=runner,
            log_id=log_id,
        )
        if result.content:
            log_text.clear()
            log_text.setPlainText(result.content)
        append_log(result.message_text)
    except Exception as exc:
        log_debug(f"Ошибка просмотра лога: {exc}")


def delete_log_history_entry(
    *,
    runner,
    current_item,
    user_role,
    update_log_history: Callable[[], None],
    append_log: Callable[[str], None],
    log_debug: Callable[[str], None],
) -> None:
    """Удаляет выбранный лог из истории."""
    if runner is None or current_item is None:
        return

    log_id = current_item.data(user_role)
    if not log_id:
        return

    try:
        result = orchestra_log_history_workflow.delete_log_history_entry(
            runner=runner,
            log_id=log_id,
        )
        if result.deleted:
            update_log_history()
        append_log(result.message_text)
    except Exception as exc:
        log_debug(f"Ошибка удаления лога: {exc}")


def clear_log_history_entries(
    *,
    runner,
    update_log_history: Callable[[], None],
    append_log: Callable[[str], None],
    log_debug: Callable[[str], None],
) -> None:
    """Удаляет все сохранённые логи orchestra."""
    if runner is None:
        return

    try:
        result = orchestra_log_history_workflow.clear_log_history_entries(
            runner=runner,
        )
        update_log_history()
        append_log(result.message_text)
    except Exception as exc:
        log_debug(f"Ошибка очистки истории логов: {exc}")
