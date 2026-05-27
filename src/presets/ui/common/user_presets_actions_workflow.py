"""Общий workflow действий для страницы пользовательских preset-ов."""

from __future__ import annotations

from qfluentwidgets import FluentIcon


def _tr_key(tr_prefix: str, suffix: str) -> str:
    return f"{tr_prefix}.{suffix}"


def show_reset_all_result(
    *,
    cleanup_in_progress: bool,
    success_count: int,
    total_count: int,
    failed_count: int = 0,
    reset_all_btn,
    single_shot_fn,
    restore_label_fn,
) -> None:
    if cleanup_in_progress:
        return
    _ = total_count
    ok = int(success_count or 0)
    failed = int(failed_count or 0)
    try:
        if failed > 0:
            reset_all_btn.setText(f"Ошибки: {failed}")
            icon = FluentIcon.INFO
        elif ok > 0:
            reset_all_btn.setText(f"Сброшено: {ok}")
            icon = FluentIcon.ACCEPT
        else:
            reset_all_btn.setText("Нечего менять")
            icon = FluentIcon.ACCEPT
        reset_all_btn.setIcon(icon)
    except Exception:
        pass
    single_shot_fn(3000, restore_label_fn)


def restore_reset_all_button_label(
    *,
    cleanup_in_progress: bool,
    reset_all_btn,
    tr_fn,
    tr_prefix: str,
) -> None:
    if cleanup_in_progress:
        return
    try:
        reset_all_btn.setText(
            tr_fn(_tr_key(tr_prefix, "button.reset_all"), "Вернуть встроенные")
        )
        reset_all_btn.setIcon(FluentIcon.RETURN)
    except Exception:
        pass
