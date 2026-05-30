from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock


class _PlainTextEditor:
    def __init__(self, text: str = "") -> None:
        self._text = str(text)
        self.plain_text_calls: list[str] = []

    def toPlainText(self) -> str:  # noqa: N802
        return self._text

    def setPlainText(self, text: str) -> None:  # noqa: N802
        value = str(text)
        self.plain_text_calls.append(value)
        self._text = value


class PresetSubpageUiGuardTests(unittest.TestCase):
    def test_raw_preset_load_skips_duplicate_plain_text_update(self) -> None:
        from presets.ui.common.preset_subpage_base import PresetRawEditorPage

        page = PresetRawEditorPage.__new__(PresetRawEditorPage)
        page._raw_load_request_id = 3
        page._preset_file_name = "Default.txt"
        page._preset_name = "Default"
        page._preset_path = None
        page._preset_origin = "user"
        page._is_loading = True
        page.editor = _PlainTextEditor("--new\n--filter-tcp=443\n")
        page._set_footer = Mock()
        page._refresh_header = Mock()

        result = SimpleNamespace(
            file_name="Default.txt",
            display_name="Default",
            path="C:/Zapret/Dev/presets/winws2/Default.txt",
            origin="user",
            text="--new\n--filter-tcp=443\n",
            footer_text="Готово",
        )

        PresetRawEditorPage._on_raw_preset_text_loaded(page, 3, result)

        self.assertEqual(page.editor.plain_text_calls, [])
        page._set_footer.assert_called_once_with("Готово")
        page._refresh_header.assert_called_once_with()
        self.assertFalse(page._is_loading)


if __name__ == "__main__":
    unittest.main()
