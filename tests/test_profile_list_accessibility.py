from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication


class ProfileListAccessibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = QApplication.instance() or QApplication([])

    def test_profile_list_has_screen_reader_name_and_help(self) -> None:
        from profile.ui.profiles_list import ProfilesList

        widget = ProfilesList()
        self.addCleanup(widget.deleteLater)

        self.assertEqual(widget.accessibleName(), "Список профилей")
        self.assertIn("стрелками вверх и вниз", widget.accessibleDescription())
        self.assertEqual(widget._view.accessibleName(), "Список профилей")
        self.assertIn("Enter открывает выбранный profile", widget._view.accessibleDescription())


if __name__ == "__main__":
    unittest.main()
