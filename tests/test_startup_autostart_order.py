from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))


class StartupAutostartOrderTests(unittest.TestCase):
    def test_theme_and_background_steps_do_not_block_startup_autostart(self) -> None:
        from main import startup_coordinator
        from main.startup_coordinator import StartupCoordinator

        class Runtime:
            def __init__(self) -> None:
                self.calls: list[str] = []

            def init_launch_runtime_api(self) -> None:
                self.calls.append("runtime_api")

            def init_launch_runtime(self) -> None:
                self.calls.append("runtime")

            def init_process_monitor(self) -> None:
                self.calls.append("process_monitor")

            def init_core_startup(self) -> None:
                self.calls.append("core_startup")

            def start_autostart(self, launch_method: str | None = None) -> None:
                self.calls.append(f"autostart:{launch_method}")

        runtime = Runtime()
        coordinator = StartupCoordinator(
            runtime_feature=runtime,
            tray_feature=SimpleNamespace(init=Mock(), is_initialized=Mock(return_value=False)),
            window_shell=SimpleNamespace(
                start_in_tray=False,
                set_status=Mock(),
                mark_startup_core_ready=Mock(),
                mark_startup_post_init_done=Mock(),
                init_theme_manager=Mock(side_effect=lambda: runtime.calls.append("theme")),
            ),
            log_startup_metric=Mock(),
        )
        scheduled: list[tuple[int, object]] = []
        background_targets: list[object] = []

        with (
            patch.object(startup_coordinator, "run_queued", side_effect=lambda callback: scheduled.append((0, callback))),
            patch.object(
                startup_coordinator.QTimer,
                "singleShot",
                side_effect=lambda delay_ms, callback: scheduled.append((int(delay_ms), callback)),
            ),
            patch.object(
                startup_coordinator,
                "start_daemon_thread",
                side_effect=lambda _name, target: background_targets.append(target),
            ),
            patch("settings.dpi.strategy_settings.get_strategy_launch_method", return_value="zapret2_mode"),
        ):
            coordinator.run_async_init()
            while scheduled:
                _delay_ms, callback = scheduled.pop(0)
                callback()

            self.assertEqual(
                runtime.calls,
                ["runtime_api", "runtime", "autostart:zapret2_mode", "theme", "process_monitor"],
            )

            self.assertEqual(len(background_targets), 1)
            background_targets[0]()
            while scheduled:
                _delay_ms, callback = scheduled.pop(0)
                callback()

        self.assertEqual(
            runtime.calls,
            ["runtime_api", "runtime", "autostart:zapret2_mode", "theme", "process_monitor", "core_startup"],
        )


if __name__ == "__main__":
    unittest.main()
