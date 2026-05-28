from __future__ import annotations

import inspect
import sys
import unittest
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))


class WindowGeometryWorkerTests(unittest.TestCase):
    def test_regular_window_geometry_saves_run_through_worker(self) -> None:
        import ui.window_geometry_runtime as runtime
        import ui.window_geometry_worker as worker_module

        self.assertTrue(hasattr(worker_module, "WindowGeometrySaveWorker"))

        worker_source = inspect.getsource(worker_module.WindowGeometrySaveWorker.run)
        persist_source = inspect.getsource(runtime.WindowGeometryRuntime._persist_geometry_now)
        max_source = inspect.getsource(runtime.WindowGeometryRuntime._persist_window_maximized_state_now)
        sync_source = inspect.getsource(runtime.WindowGeometryRuntime._persist_geometry_sync)
        request_source = inspect.getsource(runtime.WindowGeometryRuntime._request_geometry_save)

        self.assertIn("set_window_geometry", worker_source)
        self.assertIn("_persist_geometry_sync", persist_source)
        self.assertIn("_request_geometry_save", persist_source)
        self.assertIn("_request_geometry_save", max_source)
        self.assertIn("_stop_geometry_save_worker_for_sync", sync_source)
        self.assertIn("_geometry_save_pending", request_source)
        self.assertNotIn("self.store.save_geometry", persist_source)
        self.assertNotIn("self.store.save_maximized", max_source)


if __name__ == "__main__":
    unittest.main()
