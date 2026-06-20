from __future__ import annotations

from log.log import log
from main.post_startup_gate import bind_startup_gate, is_startup_host_alive
from main.post_startup_rkn_workers import run_rkn_registry_sync_worker
from main.post_startup_threading import enqueue_subsystem_task, schedule_after


RKN_SYNC_STARTUP_DELAY_MS = 20_000
RKN_SYNC_REPEAT_MS = 3_600_000


def install_rkn_registry_sync(
    startup_host,
    *,
    runtime_feature,
    log_startup_metric,
) -> None:
    timer_holder: dict[str, object] = {"timer": None}

    def _start_sync(*, force: bool = False) -> None:
        if not is_startup_host_alive(startup_host):
            return
        enqueue_subsystem_task(
            "lists",
            "RknRegistrySyncWorker",
            lambda: run_rkn_registry_sync_worker(runtime_feature=runtime_feature, force=force),
        )

    def _schedule_hourly() -> None:
        if not is_startup_host_alive(startup_host):
            return
        try:
            from lists.rkn_registry_sync import get_rkn_sync_interval_sec

            interval_ms = max(300_000, int(get_rkn_sync_interval_sec()) * 1000)
        except Exception:
            interval_ms = RKN_SYNC_REPEAT_MS

        from PyQt6.QtCore import QTimer

        timer = timer_holder.get("timer")
        if timer is None:
            timer = QTimer(startup_host._window)
            timer_holder["timer"] = timer

            def _on_timeout() -> None:
                if is_startup_host_alive(startup_host):
                    _start_sync(force=False)

            timer.timeout.connect(_on_timeout)

        timer.setInterval(interval_ms)
        if not timer.isActive():
            timer.start()
        log(f"RKN auto-update: повтор каждые {interval_ms // 1000}s", "RKN_SYNC")

    def _run_initial_sync() -> None:
        _start_sync(force=False)
        _schedule_hourly()

    def _schedule_initial_sync() -> None:
        if not is_startup_host_alive(startup_host):
            return
        try:
            from settings.store import get_rkn_lists_auto_update_enabled

            if not get_rkn_lists_auto_update_enabled():
                log("RKN auto-update отключён в настройках", "RKN_SYNC")
                return
        except Exception:
            pass

        delay_ms = RKN_SYNC_STARTUP_DELAY_MS
        log(f"RKN auto-update: первая синхронизация через {delay_ms}ms", "DEBUG")
        log_startup_metric("StartupPostInitRknSyncQueued", f"{delay_ms}ms after post-init")
        schedule_after(
            delay_ms,
            lambda: is_startup_host_alive(startup_host) and _run_initial_sync(),
        )

    bind_startup_gate(
        startup_host.startup_post_init_ready,
        _schedule_initial_sync,
        is_ready=lambda: bool(startup_host.startup_state.post_init_ready),
    )
