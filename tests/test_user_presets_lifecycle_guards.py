from __future__ import annotations

import unittest
from unittest.mock import Mock


class _TextWidget:
    def __init__(self, text: str = "") -> None:
        self._text = str(text)
        self.calls: list[str] = []

    def text(self) -> str:
        return self._text

    def setText(self, text: str) -> None:  # noqa: N802
        value = str(text)
        self.calls.append(value)
        self._text = value


class _PlaceholderWidget:
    def __init__(self, text: str = "") -> None:
        self._placeholder = str(text)
        self.calls: list[str] = []

    def placeholderText(self) -> str:  # noqa: N802
        return self._placeholder

    def setPlaceholderText(self, text: str) -> None:  # noqa: N802
        value = str(text)
        self.calls.append(value)
        self._placeholder = value


class UserPresetsLifecycleGuardTests(unittest.TestCase):
    def test_text_update_skips_duplicate_value(self) -> None:
        from presets.ui.common.user_presets_page_lifecycle import set_widget_text_if_changed

        widget = _TextWidget("Импорт")

        self.assertFalse(set_widget_text_if_changed(widget, "Импорт"))
        self.assertEqual(widget.calls, [])

        self.assertTrue(set_widget_text_if_changed(widget, "Загрузить"))
        self.assertEqual(widget.calls, ["Загрузить"])

    def test_placeholder_update_skips_duplicate_value(self) -> None:
        from presets.ui.common.user_presets_page_lifecycle import set_placeholder_if_changed

        widget = _PlaceholderWidget("Поиск пресетов по имени...")

        self.assertFalse(set_placeholder_if_changed(widget, "Поиск пресетов по имени..."))
        self.assertEqual(widget.calls, [])

        self.assertTrue(set_placeholder_if_changed(widget, "Поиск"))
        self.assertEqual(widget.calls, ["Поиск"])

    def test_page_mode_labels_skip_duplicate_text(self) -> None:
        from types import SimpleNamespace

        from presets.ui.common.user_presets_page import UserPresetsPageBase

        page = UserPresetsPageBase.__new__(UserPresetsPageBase)
        page.title_label = _TextWidget("Мои пресеты")
        page.subtitle_label = _TextWidget("")
        page._config = SimpleNamespace(title_key="page.title")
        page._tr = lambda _key, default: default

        UserPresetsPageBase._apply_mode_labels(page)

        self.assertEqual(page.title_label.calls, [])
        self.assertEqual(page.subtitle_label.calls, [])

    def test_sidebar_search_skips_duplicate_query_refresh(self) -> None:
        from presets.ui.common.user_presets_page import UserPresetsPageBase

        page = UserPresetsPageBase.__new__(UserPresetsPageBase)
        page._preset_search_input = _TextWidget("Discord")
        page._apply_preset_search = Mock(side_effect=AssertionError("same search query must not refresh presets"))

        self.assertTrue(UserPresetsPageBase.apply_sidebar_search_query(page, "Discord"))

        page._apply_preset_search.assert_not_called()


if __name__ == "__main__":
    unittest.main()
