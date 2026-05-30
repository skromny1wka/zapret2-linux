import inspect
import unittest

from blockcheck.ui.strategy_scan_page import StrategyScanPage


class StrategyScanApplyRuntimeArchitectureTests(unittest.TestCase):
    def test_strategy_apply_uses_runtime_not_manual_page_worker(self) -> None:
        page_source = inspect.getsource(StrategyScanPage)
        request_source = inspect.getsource(StrategyScanPage._request_strategy_apply)
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


if __name__ == "__main__":
    unittest.main()
