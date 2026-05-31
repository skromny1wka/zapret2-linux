from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))


class DpiSettingsWorkerQueueTests(unittest.TestCase):
    def test_dpi_settings_pending_restarts_after_event_loop_turn(self) -> None:
        import settings.dpi.page as dpi_page
        from settings.dpi.page import DpiSettingsPage

        page = DpiSettingsPage.__new__(DpiSettingsPage)
        page._cleanup_in_progress = False
        page._dpi_settings_pending = [("apply_launch_method", "zapret2_mode")]
        page._start_dpi_settings_worker = Mock()
        single_shot = Mock(side_effect=lambda _delay, _callback: None)

        with patch.object(dpi_page, "QTimer", SimpleNamespace(singleShot=single_shot), create=True):
            DpiSettingsPage._on_dpi_settings_worker_finished(page, object())

        single_shot.assert_called_once()
        self.assertEqual(single_shot.call_args.args[0], 0)
        page._start_dpi_settings_worker.assert_not_called()

        single_shot.call_args.args[1]()

        page._start_dpi_settings_worker.assert_called_once_with(("apply_launch_method", "zapret2_mode"))

    def test_orchestra_setting_pending_restarts_after_event_loop_turn(self) -> None:
        import settings.dpi.page as dpi_page
        from settings.dpi.page import DpiSettingsPage

        page = DpiSettingsPage.__new__(DpiSettingsPage)
        page._cleanup_in_progress = False
        page._orchestra_settings_save_pending = [("debug_file", True)]
        page._start_orchestra_setting_save_worker = Mock()
        single_shot = Mock(side_effect=lambda _delay, _callback: None)

        with patch.object(dpi_page, "QTimer", SimpleNamespace(singleShot=single_shot), create=True):
            DpiSettingsPage._on_orchestra_setting_save_worker_finished(page, object())

        single_shot.assert_called_once()
        self.assertEqual(single_shot.call_args.args[0], 0)
        page._start_orchestra_setting_save_worker.assert_not_called()

        single_shot.call_args.args[1]()

        page._start_orchestra_setting_save_worker.assert_called_once_with(("debug_file", True))


if __name__ == "__main__":
    unittest.main()
