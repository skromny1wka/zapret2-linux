import inspect
import unittest

from updater.update_page_runtime import UpdatePageRuntime


class UpdaterInstallRuntimeArchitectureTest(unittest.TestCase):
    def test_update_install_worker_runs_through_shared_runtime(self) -> None:
        runtime_source = inspect.getsource(UpdatePageRuntime)
        init_source = inspect.getsource(UpdatePageRuntime.__init__)
        start_source = inspect.getsource(UpdatePageRuntime._start_update_download)
        create_source = inspect.getsource(UpdatePageRuntime._create_update_worker_runtime)
        bind_source = inspect.getsource(UpdatePageRuntime._bind_update_worker_signals)
        teardown_source = inspect.getsource(UpdatePageRuntime._teardown_update_runtime)

        self.assertIn("_update_install_runtime = OneShotWorkerRuntime()", init_source)
        self.assertIn("start_qobject_worker", start_source)
        self.assertIn("bind_worker=self._bind_update_worker_signals", start_source)
        self.assertIn("on_finished=self._handle_update_install_finished", start_source)
        self.assertIn("create_update_install_worker", create_source)
        self.assertIn("_update_install_runtime.stop", teardown_source)
        self.assertNotIn("QThread", runtime_source)
        self.assertNotIn("thread.start()", runtime_source)
        self.assertNotIn("moveToThread", create_source)
        self.assertNotIn("thread.started.connect", bind_source)
        self.assertNotIn("self._update_thread", runtime_source)
        self.assertNotIn("self._update_worker", runtime_source)


if __name__ == "__main__":
    unittest.main()
