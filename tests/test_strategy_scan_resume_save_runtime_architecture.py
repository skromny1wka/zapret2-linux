import inspect
import unittest

from blockcheck.ui.strategy_scan_page import StrategyScanPage


class StrategyScanResumeSaveRuntimeArchitectureTests(unittest.TestCase):
    def test_resume_save_uses_runtime_not_manual_page_worker(self) -> None:
        page_source = inspect.getsource(StrategyScanPage)
        request_source = inspect.getsource(StrategyScanPage._request_strategy_scan_resume_save)
        start_source = inspect.getsource(StrategyScanPage._start_strategy_scan_resume_save_worker)
        finished_source = inspect.getsource(StrategyScanPage._on_strategy_scan_resume_save_finished)
        failed_source = inspect.getsource(StrategyScanPage._on_strategy_scan_resume_save_failed)
        runtime_finished = getattr(
            StrategyScanPage,
            "_on_strategy_scan_resume_save_runtime_finished",
            None,
        )
        runtime_finished_source = inspect.getsource(runtime_finished) if runtime_finished else ""
        cleanup_source = inspect.getsource(StrategyScanPage.cleanup)

        self.assertIn("_strategy_scan_resume_save_runtime = OneShotWorkerRuntime()", page_source)
        self.assertIn("_strategy_scan_resume_save_runtime.is_running()", request_source)
        self.assertIn("start_qthread_worker", start_source)
        self.assertIn("bind_worker", start_source)
        self.assertIn("_on_strategy_scan_resume_save_runtime_finished", start_source)
        self.assertIn("_strategy_scan_resume_save_runtime.is_current", finished_source)
        self.assertIn("_strategy_scan_resume_save_runtime.is_current", failed_source)
        self.assertIn("_strategy_scan_resume_save_pending", runtime_finished_source)
        self.assertIn("_strategy_scan_resume_save_runtime.stop", cleanup_source)
        self.assertIn("_strategy_scan_resume_save_runtime.cancel", cleanup_source)
        self.assertNotIn("_strategy_scan_resume_save_worker =", page_source)
        self.assertNotIn("_strategy_scan_resume_save_request_id", page_source)
        self.assertNotIn("worker.start()", start_source)


if __name__ == "__main__":
    unittest.main()
