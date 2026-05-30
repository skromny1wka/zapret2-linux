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
        import main.window_lifecycle_setup as lifecycle_setup
        from app.feature_facades.window_geometry import WindowGeometryFeature
        import ui.window_geometry_runtime as runtime
        import app.window_geometry_workers as worker_module

        self.assertTrue(hasattr(worker_module, "WindowGeometrySaveWorker"))

        worker_source = inspect.getsource(worker_module.WindowGeometrySaveWorker.run)
        feature_source = inspect.getsource(WindowGeometryFeature)
        lifecycle_source = inspect.getsource(lifecycle_setup.attach_window_lifecycle)
        runtime_source = inspect.getsource(runtime.WindowGeometryRuntime)
        persist_source = inspect.getsource(runtime.WindowGeometryRuntime._persist_geometry_now)
        max_source = inspect.getsource(runtime.WindowGeometryRuntime._persist_window_maximized_state_now)
        sync_source = inspect.getsource(runtime.WindowGeometryRuntime._persist_geometry_sync)
        request_source = inspect.getsource(runtime.WindowGeometryRuntime._request_geometry_save)

        self.assertIn("set_window_geometry=self.set_window_geometry", feature_source)
        self.assertIn("get_window_geometry=self.get_window_geometry", feature_source)
        self.assertIn("features.window_geometry.create_geometry_save_worker", lifecycle_source)
        self.assertIn("create_geometry_save_worker", runtime_source)
        self.assertNotIn("ui.window_geometry_worker", runtime_source)
        self.assertNotIn("settings_store", worker_source)
        self.assertIn("_persist_geometry_sync", persist_source)
        self.assertIn("_request_geometry_save", persist_source)
        self.assertIn("_request_geometry_save", max_source)
        self.assertIn("_stop_geometry_save_worker_for_sync", sync_source)
        self.assertIn("_geometry_save_pending", request_source)
        self.assertNotIn("self.store.save_geometry", persist_source)
        self.assertNotIn("self.store.save_maximized", max_source)


if __name__ == "__main__":
    unittest.main()
