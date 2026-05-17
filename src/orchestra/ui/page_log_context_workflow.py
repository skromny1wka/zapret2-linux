"""Workflow контекстного меню лога orchestra-страницы."""

from __future__ import annotations

from PyQt6.QtWidgets import QApplication
from qfluentwidgets import Action, RoundMenu

import orchestra.page_runtime as orchestra_page_runtime
import orchestra.log_context_actions as orchestra_log_context_actions
from log.log import log
from ui.popup_menu import exec_popup_menu


def parse_log_line_for_strategy(line: str) -> tuple[str, int, str] | None:
    parsed = orchestra_page_runtime.parse_log_line_for_strategy(line)
    if parsed is None:
        return None
    return (parsed.domain, parsed.strategy, parsed.protocol)


def show_log_context_menu(
    *,
    owner,
    log_text,
    pos,
    runner,
    tr_fn,
    copy_line_fn,
    lock_strategy_fn,
    block_strategy_fn,
    unblock_strategy_fn,
    add_to_whitelist_fn,
) -> None:
    cursor = log_text.cursorForPosition(pos)
    cursor.select(cursor.SelectionType.LineUnderCursor)
    line_text = cursor.selectedText().strip()
    if not line_text:
        return

    parsed = parse_log_line_for_strategy(line_text)
    menu = RoundMenu(parent=owner)

    if parsed:
        domain, strategy, protocol = parsed
        is_blocked = False
        try:
            is_blocked = orchestra_log_context_actions.is_strategy_blocked(
                runner=runner,
                domain=domain,
                strategy=strategy,
            )
        except Exception:
            pass

        context_plan = orchestra_page_runtime.build_context_menu_plan(
            domain=domain,
            strategy=strategy,
            is_blocked=is_blocked,
            copy_label=tr_fn("page.orchestra.context.copy_line", "📋 Копировать строку"),
            lock_label=tr_fn(
                "page.orchestra.context.lock_strategy",
                "🔒 Залочить стратегию #{strategy} для {domain}",
                strategy=strategy,
                domain=domain,
            ) if strategy > 0 else None,
            block_label=tr_fn(
                "page.orchestra.context.block_strategy",
                "🚫 Заблокировать стратегию #{strategy} для {domain}",
                strategy=strategy,
                domain=domain,
            ) if strategy > 0 else None,
            unblock_label=tr_fn(
                "page.orchestra.context.unblock_strategy",
                "✅ Разблокировать стратегию #{strategy} для {domain}",
                strategy=strategy,
                domain=domain,
            ) if strategy > 0 else None,
            whitelist_label=tr_fn(
                "page.orchestra.context.add_whitelist",
                "⬚ Добавить {domain} в белый список",
                domain=domain,
            ),
        )
    else:
        context_plan = orchestra_page_runtime.build_context_menu_plan(
            domain=None,
            strategy=None,
            is_blocked=False,
            copy_label=tr_fn("page.orchestra.context.copy_line", "📋 Копировать строку"),
            lock_label=None,
            block_label=None,
            unblock_label=None,
            whitelist_label=None,
        )

    actions_by_id: dict[str, Action] = {}
    for action_plan in context_plan.actions:
        action = Action(action_plan.label, owner)
        actions_by_id[action_plan.action_id] = action
        menu.addAction(action)

    copy_action = actions_by_id.get("copy")
    if copy_action is not None:
        copy_action.triggered.connect(lambda: copy_line_fn(line_text))

    if parsed and context_plan.has_strategy_actions:
        domain, strategy, protocol = parsed
        menu.insertSeparator(actions_by_id.get("copy"))
        if "lock" in actions_by_id:
            actions_by_id["lock"].triggered.connect(lambda: lock_strategy_fn(domain, strategy, protocol))
        if "block" in actions_by_id:
            actions_by_id["block"].triggered.connect(lambda: block_strategy_fn(domain, strategy, protocol))
        if "unblock" in actions_by_id:
            actions_by_id["unblock"].triggered.connect(lambda: unblock_strategy_fn(domain, strategy, protocol))
        if "whitelist" in actions_by_id:
            actions_by_id["whitelist"].triggered.connect(lambda: add_to_whitelist_fn(domain))

    exec_popup_menu(menu, log_text.mapToGlobal(pos), owner=owner)


def copy_line_to_clipboard(*, text: str, append_log, tr_fn) -> None:
    clipboard = QApplication.clipboard()
    if clipboard is None:
        return
    clipboard.setText(text)
    append_log(tr_fn("page.orchestra.log.clipboard_copied", "[INFO] Строка скопирована в буфер обмена"))


def lock_strategy_from_log(*, runner, domain: str, strategy: int, protocol: str, append_log, refresh_learned, tr_fn) -> None:
    try:
        plan = orchestra_log_context_actions.lock_strategy_from_log(
            runner=runner,
            domain=domain,
            strategy=strategy,
            protocol=protocol,
        )
        _apply_runner_action_plan(plan, append_log=append_log, refresh_learned=refresh_learned)
    except Exception as exc:
        log(f"Ошибка залочивания из контекстного меню: {exc}", "ERROR")
        append_log(tr_fn("page.orchestra.log.error", "[ERROR] Ошибка: {error}", error=exc))


def block_strategy_from_log(*, runner, domain: str, strategy: int, protocol: str, append_log, refresh_learned, tr_fn) -> None:
    try:
        plan = orchestra_log_context_actions.block_strategy_from_log(
            runner=runner,
            domain=domain,
            strategy=strategy,
            protocol=protocol,
        )
        _apply_runner_action_plan(plan, append_log=append_log, refresh_learned=refresh_learned)
    except Exception as exc:
        log(f"Ошибка блокировки из контекстного меню: {exc}", "ERROR")
        append_log(tr_fn("page.orchestra.log.error", "[ERROR] Ошибка: {error}", error=exc))


def unblock_strategy_from_log(*, runner, domain: str, strategy: int, protocol: str, append_log, refresh_learned, tr_fn) -> None:
    try:
        plan = orchestra_log_context_actions.unblock_strategy_from_log(
            runner=runner,
            domain=domain,
            strategy=strategy,
            protocol=protocol,
        )
        _apply_runner_action_plan(plan, append_log=append_log, refresh_learned=refresh_learned)
    except Exception as exc:
        log(f"Ошибка разблокировки из контекстного меню: {exc}", "ERROR")
        append_log(tr_fn("page.orchestra.log.error", "[ERROR] Ошибка: {error}", error=exc))


def add_to_whitelist_from_log(*, runner, domain: str, append_log, tr_fn) -> None:
    try:
        plan = orchestra_log_context_actions.add_to_whitelist_from_log(runner=runner, domain=domain)
        for message in plan.messages:
            append_log(message)
    except Exception as exc:
        log(f"Ошибка добавления в whitelist из контекстного меню: {exc}", "ERROR")
        append_log(tr_fn("page.orchestra.log.error", "[ERROR] Ошибка: {error}", error=exc))


def _apply_runner_action_plan(plan, *, append_log, refresh_learned) -> None:
    for message in plan.messages:
        append_log(message)
    if plan.refresh_learned:
        refresh_learned()
