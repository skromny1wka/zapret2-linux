from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget

from ui.pages.about_page_support_build import build_about_page_support_content
from ui.theme import get_theme_tokens


class AboutSupportAccessibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = QApplication.instance() or QApplication([])

    def test_support_cards_have_screen_reader_text(self) -> None:
        parent = QWidget()
        layout = QVBoxLayout(parent)

        widgets = build_about_page_support_content(
            layout,
            tr_fn=lambda _key, default: default,
            content_parent=parent,
            tokens=get_theme_tokens(),
            on_open_discussions=lambda: None,
            on_open_telegram=lambda: None,
            on_open_discord=lambda: None,
        )

        self.assertEqual(widgets.discussions_card.accessibleName(), "Открыть GitHub Discussions")
        self.assertIn("Основной канал поддержки", widgets.discussions_card.accessibleDescription())
        self.assertEqual(widgets.telegram_card.accessibleName(), "Открыть Telegram")
        self.assertIn("сообществом", widgets.telegram_card.accessibleDescription())
        self.assertEqual(widgets.discord_card.accessibleName(), "Открыть Discord")
        self.assertIn("живое общение", widgets.discord_card.accessibleDescription())


if __name__ == "__main__":
    unittest.main()
