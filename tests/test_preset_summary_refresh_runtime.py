from __future__ import annotations

import inspect
import unittest


class PresetSummaryRefreshRuntimeTests(unittest.TestCase):
    def test_summary_refresh_uses_one_shot_worker_runtime(self) -> None:
        from presets.display_state_refresh import PresetProfileStrategySummaryRefreshRuntime

        init_source = inspect.getsource(PresetProfileStrategySummaryRefreshRuntime.__init__)
        request_source = inspect.getsource(PresetProfileStrategySummaryRefreshRuntime.request_refresh)
        start_source = inspect.getsource(PresetProfileStrategySummaryRefreshRuntime._start_worker)
        finish_source = inspect.getsource(PresetProfileStrategySummaryRefreshRuntime._on_worker_finished)
        cleanup_source = inspect.getsource(PresetProfileStrategySummaryRefreshRuntime.cleanup)
        class_source = inspect.getsource(PresetProfileStrategySummaryRefreshRuntime)

        self.assertIn("OneShotWorkerRuntime", init_source)
        self.assertIn("_summary_runtime", class_source)
        self.assertIn("_summary_runtime.is_running()", request_source)
        self.assertIn("start_qthread_worker", start_source)
        self.assertNotIn("worker.start()", start_source)
        self.assertNotIn("self._worker", class_source)
        self.assertNotIn("worker.deleteLater()", finish_source)
        self.assertIn("_summary_runtime.stop", cleanup_source)
        self.assertIn("_summary_runtime.cancel", cleanup_source)

    def test_window_close_cleans_up_summary_refresh_runtime(self) -> None:
        import main.application_lifecycle_port as lifecycle_port
        import main.window_lifecycle_cleanup as lifecycle_cleanup

        port_source = inspect.getsource(lifecycle_port.ApplicationLifecycleWindowPort.cleanup_threaded_pages)
        cleanup_source = inspect.getsource(lifecycle_cleanup.cleanup_session_runtimes_for_close)

        self.assertIn("cleanup_session_runtimes_for_close", port_source)
        self.assertIn("preset_summary_refresh_runtime", cleanup_source)
        self.assertIn("runtime.cleanup()", cleanup_source)


if __name__ == "__main__":
    unittest.main()
