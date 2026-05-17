from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import threading
import tempfile
import unittest
from unittest.mock import Mock, patch


class Winws2PresetSwitchTests(unittest.TestCase):
    def test_fast_switch_cleans_existing_winws_process_not_owned_by_runner(self) -> None:
        from winws_runtime.runners.zapret2_runner import Winws2StrategyRunner

        with tempfile.TemporaryDirectory() as tmp_dir:
            preset_path = Path(tmp_dir) / "selected.txt"
            preset_path.write_text("--wf-tcp-out=80", encoding="utf-8")

            runner = object.__new__(Winws2StrategyRunner)
            runner._state_lock = threading.RLock()
            runner.running_process = None
            runner._preset_file_path = ""
            runner._set_last_error = Mock()
            runner._stop_config_watcher = Mock()
            runner._compile_preset_artifact = Mock(
                return_value=SimpleNamespace(
                    validation_ok=True,
                    validation_report="",
                    preset_path=str(preset_path),
                )
            )
            runner._spawn_process_locked = Mock(return_value=True)
            runner._start_config_watcher = Mock()
            runner._perform_standard_windivert_cleanup = Mock()

            with patch(
                "winws_runtime.runners.zapret2_runner.get_all_winws_process_pids",
                return_value=[777],
            ):
                self.assertTrue(runner.switch_preset_file_fast(str(preset_path), "Selected"))

            runner._perform_standard_windivert_cleanup.assert_called_once()
            runner._spawn_process_locked.assert_called_once()


if __name__ == "__main__":
    unittest.main()
