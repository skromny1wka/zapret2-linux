from __future__ import annotations

import os
import time

from log.log import log
from settings.mode import (
    exe_name_for_launch_method,
    exe_path_for_launch_method,
    is_orchestra_launch_method,
    normalize_launch_method,
)


def init_launch_runtime_api(app) -> None:
    from settings.dpi.strategy_settings import get_strategy_launch_method
    from winws_runtime.runtime.runtime_api import PresetLaunchRuntimeApi

    launch_method = get_strategy_launch_method()
    winws_exe = exe_path_for_launch_method(launch_method)
    exe_name = exe_name_for_launch_method(launch_method)
    log(f"Используется {exe_name} для режима {launch_method}", "INFO")

    app.launch_runtime_api = PresetLaunchRuntimeApi(
        expected_exe_path=winws_exe,
        status_callback=app.set_status,
        app_instance=app,
    )
    log("Launch runtime API инициализирован", "INFO")


def init_launch_controller(app) -> None:
    from winws_runtime.runtime.controller import PresetLaunchController

    app.launch_controller = PresetLaunchController(app)
    log("Launch controller инициализирован", "INFO")


def init_process_monitor(app) -> None:
    started_at = time.perf_counter()

    app.process_monitor_manager.initialize_process_monitor()

    try:
        from settings.dpi.strategy_settings import get_strategy_launch_method

        launch_method = normalize_launch_method(get_strategy_launch_method())
        expected_process = ""
        target_exe = exe_path_for_launch_method(launch_method)
        if not is_orchestra_launch_method(launch_method):
            expected_process = os.path.basename(target_exe).strip().lower()

        app.launch_runtime_api.set_expected_exe_path(target_exe)
        app.launch_runtime_service.bootstrap_probe(
            app.launch_runtime_api.is_expected_running(silent=True),
            launch_method=launch_method,
            expected_process=expected_process,
        )
    except Exception as exc:
        log(f"Ошибка начальной проверки process monitor: {exc}", "DEBUG")

    log(f"✅ Process monitor: {(time.perf_counter() - started_at) * 1000:.0f}ms", "DEBUG")


def init_core_startup(app) -> None:
    started_at = time.perf_counter()

    from lists.file_manager import ensure_required_files

    ensure_required_files()
    app.last_strategy_change_time = time.time()

    log(f"✅ Core startup: {(time.perf_counter() - started_at) * 1000:.0f}ms", "DEBUG")
