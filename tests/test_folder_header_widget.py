from __future__ import annotations

import unittest

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QFont

from ui.widgets.folder_header import (
    FOLDER_HEADER_GAP,
    FOLDER_HEADER_ICON_BOX,
    FOLDER_HEADER_LEFT_MARGIN,
    FOLDER_HEADER_RIGHT_MARGIN,
    FOLDER_HEADER_STYLE_SHEET,
    folder_header_font,
    folder_header_icon_name,
    folder_header_title,
    is_folder_toggle_click,
)


class _Event:
    def __init__(self, event_type, button):
        self._event_type = event_type
        self._button = button

    def type(self):
        return self._event_type

    def button(self):
        return self._button


class FolderHeaderTests(unittest.TestCase):
    def test_icon_name_matches_expanded_state(self) -> None:
        self.assertEqual(folder_header_icon_name(True), "fa5s.chevron-down")
        self.assertEqual(folder_header_icon_name(False), "fa5s.chevron-right")

    def test_title_appends_count_like_gui_folder_header(self) -> None:
        self.assertEqual(folder_header_title("YouTube", 3), "YouTube  3")
        self.assertEqual(folder_header_title("YouTube", 0), "YouTube")
        self.assertEqual(folder_header_title("YouTube", -1), "YouTube")

    def test_folder_toggles_only_on_left_mouse_release(self) -> None:
        self.assertTrue(is_folder_toggle_click(_Event(QEvent.Type.MouseButtonRelease, Qt.MouseButton.LeftButton)))
        self.assertFalse(is_folder_toggle_click(_Event(QEvent.Type.MouseButtonPress, Qt.MouseButton.LeftButton)))
        self.assertFalse(is_folder_toggle_click(_Event(QEvent.Type.MouseButtonRelease, Qt.MouseButton.RightButton)))

    def test_widget_and_painted_folder_header_share_style_constants(self) -> None:
        self.assertEqual(FOLDER_HEADER_LEFT_MARGIN, 0)
        self.assertEqual(FOLDER_HEADER_RIGHT_MARGIN, 8)
        self.assertEqual(FOLDER_HEADER_ICON_BOX, 16)
        self.assertEqual(FOLDER_HEADER_GAP, 4)
        self.assertIn('QFrame[folderHeader="true"]', FOLDER_HEADER_STYLE_SHEET)

    def test_folder_header_font_uses_shared_weight(self) -> None:
        self.assertEqual(folder_header_font(QFont()).weight(), QFont.Weight.DemiBold)


if __name__ == "__main__":
    unittest.main()
