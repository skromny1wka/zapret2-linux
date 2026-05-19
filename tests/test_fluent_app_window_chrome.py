from __future__ import annotations

import os
import inspect
import unittest


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from ui.fluent_app_window import ZapretFluentWindow


class FluentAppWindowChromeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = QApplication.instance() or QApplication([])

    def test_window_uses_qfluentwidgets_content_margins_without_resize_compensation(self) -> None:
        window = ZapretFluentWindow()
        margins = window.widgetLayout.contentsMargins()

        self.assertEqual(margins.top(), 48)
        self.assertEqual(margins.right(), 0)
        self.assertEqual(margins.bottom(), 0)

    def test_window_chrome_has_no_legacy_border_radius_or_handle_hooks(self) -> None:
        source = inspect.getsource(ZapretFluentWindow)

        self.assertNotIn("WINDOW_RESIZE_SAFE_MARGIN", source)
        self.assertNotIn("_apply_window_content_margins", source)
        self.assertNotIn("_update_border_radius", source)
        self.assertNotIn("_set_handles_visible", source)
        self.assertFalse(hasattr(ZapretFluentWindow, "set_zoom_chrome_compact"))


if __name__ == "__main__":
    unittest.main()
