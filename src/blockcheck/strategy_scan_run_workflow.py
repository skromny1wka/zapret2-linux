"""Workflow запуска и остановки подбора стратегии BlockCheck."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from collections.abc import Callable


@dataclass(frozen=True)
class StrategyScanRunStartResult:
    worker: object
    run_log_file: Path | None
    target: str
    scan_protocol: str
    udp_games_scope: str
    mode: str
    scan_cursor: int
    keep_current_results: bool
    status_text: str


def start_strategy_scan_run(
    *,
    blockcheck_feature,
    runtime_feature,
    raw_target_input: str,
    raw_protocol_value,
    raw_udp_scope_value,
    mode_index: int,
    previous_target: str,
    previous_protocol: str,
    previous_scope: str,
    result_rows_count: int,
    table_row_count: int,
    starting_status_text: str,
    parent,
    on_strategy_started,
    on_strategy_result,
    on_log,
    on_phase_changed,
    on_finished,
) -> StrategyScanRunStartResult:
    """Готовит состояние и worker подбора стратегии."""
    selection = blockcheck_feature.build_selection_state(
        protocol_value=raw_protocol_value,
        udp_scope_value=raw_udp_scope_value,
        mode_index=mode_index,
    )
    start_plan = blockcheck_feature.plan_scan_start(
        raw_target_input=raw_target_input,
        scan_protocol=selection.scan_protocol,
        udp_games_scope=selection.udp_games_scope,
        mode=selection.mode,
        previous_target=previous_target,
        previous_protocol=previous_protocol,
        previous_scope=previous_scope,
        result_rows_count=result_rows_count,
        table_row_count=table_row_count,
        starting_status_text=starting_status_text,
    )
    log_state = blockcheck_feature.start_run_log(
        target=start_plan.target,
        mode=start_plan.mode,
        scan_protocol=start_plan.scan_protocol,
        resume_index=start_plan.scan_cursor,
        udp_games_scope=start_plan.udp_games_scope,
    )

    worker = blockcheck_feature.create_strategy_scan_worker(
        target=start_plan.target,
        mode=start_plan.mode,
        start_index=start_plan.scan_cursor,
        scan_protocol=start_plan.scan_protocol,
        udp_games_scope=start_plan.udp_games_scope,
        runtime_feature=runtime_feature,
        parent=parent,
    )
    worker.strategy_started.connect(on_strategy_started)
    worker.strategy_result.connect(on_strategy_result)
    worker.scan_log.connect(on_log)
    worker.phase_changed.connect(on_phase_changed)
    worker.scan_finished.connect(on_finished)

    return StrategyScanRunStartResult(
        worker=worker,
        run_log_file=log_state.path,
        target=start_plan.target,
        scan_protocol=start_plan.scan_protocol,
        udp_games_scope=start_plan.udp_games_scope,
        mode=start_plan.mode,
        scan_cursor=start_plan.scan_cursor,
        keep_current_results=start_plan.keep_current_results,
        status_text=start_plan.status_text,
    )


def start_strategy_scan_worker(worker) -> None:
    """Запускает уже подготовленный worker подбора стратегии."""
    worker.start()


def record_strategy_scan_result(
    *,
    blockcheck_feature,
    scan_target: str,
    scan_protocol: str,
    scan_udp_games_scope: str,
    scan_cursor: int,
) -> int:
    """Сохраняет позицию продолжения после результата стратегии."""
    next_cursor = int(scan_cursor) + 1
    blockcheck_feature.save_resume_state(
        scan_target,
        scan_protocol,
        next_cursor,
        scan_udp_games_scope,
    )
    return next_cursor


def append_strategy_scan_log(*, blockcheck_feature, run_log_file, message: str) -> None:
    """Записывает строку в лог подбора стратегии."""
    blockcheck_feature.append_run_log(run_log_file, message)


def record_strategy_scan_phase(*, blockcheck_feature, run_log_file, phase: str) -> None:
    """Записывает phase-событие в лог подбора стратегии."""
    blockcheck_feature.append_run_log(run_log_file, f"[PHASE] {phase}")


def finalize_strategy_scan(
    *,
    blockcheck_feature,
    report,
    scan_target: str,
    scan_protocol: str,
    scan_udp_games_scope: str,
    scan_mode: str,
    scan_cursor: int,
    result_rows: list[dict],
    run_log_file,
):
    """Финализирует отчёт подбора стратегии и записывает итог в лог."""
    finish_plan = blockcheck_feature.finalize_scan_report(
        report,
        scan_target=scan_target,
        scan_protocol=scan_protocol,
        scan_udp_games_scope=scan_udp_games_scope,
        scan_mode=scan_mode,
        scan_cursor=scan_cursor,
        result_rows=result_rows,
    )
    if finish_plan.log_message:
        blockcheck_feature.append_run_log(run_log_file, finish_plan.log_message)
    return finish_plan


def record_strategy_scan_force_stop_warning(
    *,
    blockcheck_feature,
    run_log_file,
    warning_text: str,
) -> None:
    """Записывает предупреждение о долгой остановке подбора стратегии."""
    blockcheck_feature.append_run_log(run_log_file, f"WARNING: {warning_text}")


def delete_strategy_scan_worker_later(worker) -> None:
    """Планирует удаление worker-а после завершения сканирования."""
    if worker is None:
        return
    try:
        worker.deleteLater()
    except Exception:
        pass


def request_strategy_scan_stop(
    *,
    worker,
    schedule_stop_check: Callable[[object | None], None],
) -> None:
    """Запрашивает остановку worker-а подбора стратегии."""
    expected_worker = None
    if worker is not None:
        worker.stop()
        expected_worker = worker
    schedule_stop_check(expected_worker)


def cleanup_strategy_scan_worker(worker):
    """Останавливает или удаляет worker при закрытии страницы."""
    if worker is None:
        return None
    try:
        worker.stop()
    except Exception:
        pass
    if not getattr(worker, "is_running", False):
        try:
            worker.deleteLater()
        except Exception:
            pass
        return None
    return worker
