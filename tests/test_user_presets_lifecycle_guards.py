from __future__ import annotations

import unittest


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


if __name__ == "__main__":
    unittest.main()
