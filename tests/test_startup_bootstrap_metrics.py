from __future__ import annotations

import inspect
import unittest


class StartupBootstrapMetricsTests(unittest.TestCase):
    def test_qt_runtime_logs_bootstrap_substeps(self) -> None:
        from main import qt_runtime

        source = "\n".join(
            (
                inspect.getsource(qt_runtime.ensure_qt_runtime),
                inspect.getsource(qt_runtime.application_bootstrap),
            )
        )

        self.assertIn("StartupQtRuntimeQApplication", source)
        self.assertIn("StartupQtRuntimeReadyHooks", source)
        self.assertIn("StartupQtCrashHandler", source)
        self.assertIn("StartupQtThemeMode", source)
        self.assertIn("StartupQtAccent", source)

    def test_window_constructor_logs_bootstrap_substeps(self) -> None:
        from main.window_startup import WindowStartupMixin
        from ui.fluent_app_window import ZapretFluentWindow

        source = "\n".join(
            (
                inspect.getsource(WindowStartupMixin.__init__),
                inspect.getsource(ZapretFluentWindow.__init__),
            )
        )

        self.assertIn("StartupWindowCtorSuper", source)
        self.assertIn("StartupWindowLaunchMethod", source)
        self.assertIn("StartupFluentWindowSuper", source)
        self.assertIn("StartupFluentWindowIcon", source)

    def test_application_controller_logs_runtime_and_attach_substeps(self) -> None:
        from main.application_controller import ApplicationController

        source = inspect.getsource(ApplicationController.create_window)

        self.assertIn("StartupAppRuntimeBuild", source)
        self.assertIn("StartupWindowAttachRuntime", source)


if __name__ == "__main__":
    unittest.main()
