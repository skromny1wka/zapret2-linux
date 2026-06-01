import inspect
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from blockcheck.ui.strategy_scan_page import StrategyScanPage


class StrategyScanApplyRuntimeArchitectureTests(unittest.TestCase):
    def test_strategy_apply_uses_runtime_not_manual_page_worker(self) -> None:
        page_source = inspect.getsource(StrategyScanPage)
        request_source = "\n".join(
            (
                inspect.getsource(StrategyScanPage._request_strategy_apply),
                inspect.getsource(StrategyScanPage._start_strategy_apply_worker),
            )
        )
        finished_source = inspect.getsource(StrategyScanPage._on_strategy_apply_finished)
        failed_source = inspect.getsource(StrategyScanPage._on_strategy_apply_failed)
        cleanup_source = inspect.getsource(StrategyScanPage.cleanup)

        self.assertIn("_strategy_apply_runtime = OneShotWorkerRuntime()", page_source)
        self.assertIn("_strategy_apply_runtime.is_running()", request_source)
        self.assertIn("start_qthread_worker", request_source)
        self.assertIn("bind_worker", request_source)
        self.assertIn("_strategy_apply_runtime.is_current", finished_source)
        self.assertIn("_strategy_apply_runtime.is_current", failed_source)
        self.assertIn("_strategy_apply_runtime.stop", cleanup_source)
        self.assertIn("_strategy_apply_runtime.cancel", cleanup_source)
        self.assertNotIn("_strategy_apply_worker =", page_source)
        self.assertNotIn("_strategy_apply_request_id", page_source)
        self.assertNotIn("worker.start()", request_source)

    def test_strategy_apply_queues_latest_request_while_worker_runs(self) -> None:
        class _Runtime:
            def is_running(self) -> bool:
                return True

        page = StrategyScanPage.__new__(StrategyScanPage)
        page._strategy_apply_runtime = _Runtime()
        page._strategy_apply_pending = None
        page._strategy_apply_start_scheduled = False
        page.create_strategy_apply_worker = Mock()

        StrategyScanPage._request_strategy_apply(page, "--dpi-desync=fake", "old")
        StrategyScanPage._request_strategy_apply(page, "--dpi-desync=split", "new")

        page.create_strategy_apply_worker.assert_not_called()
        self.assertEqual(
            page._strategy_apply_pending,
            {
                "strategy_args": "--dpi-desync=split",
                "strategy_name": "new",
            },
        )

    def test_strategy_apply_pending_restarts_after_event_loop_turn(self) -> None:
        import blockcheck.ui.strategy_scan_page as strategy_scan_page

        pending = {
            "strategy_args": "--dpi-desync=split",
            "strategy_name": "new",
        }
        page = StrategyScanPage.__new__(StrategyScanPage)
        page._cleanup_in_progress = False
        page._strategy_apply_pending = pending
        page._strategy_apply_start_scheduled = False
        page._start_strategy_apply_worker = Mock()
        single_shot = Mock(side_effect=lambda _delay, _callback: None)

        with patch.object(strategy_scan_page, "QTimer", SimpleNamespace(singleShot=single_shot), create=True):
            StrategyScanPage._on_strategy_apply_runtime_finished(page, object())

        single_shot.assert_called_once()
        self.assertEqual(single_shot.call_args.args[0], 0)
        page._start_strategy_apply_worker.assert_not_called()

        single_shot.call_args.args[1]()

        page._start_strategy_apply_worker.assert_called_once_with(pending)
        self.assertIsNone(page._strategy_apply_pending)


if __name__ == "__main__":
    unittest.main()
