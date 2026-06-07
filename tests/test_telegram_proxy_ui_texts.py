from __future__ import annotations

import unittest


class TelegramProxyUiTextsTests(unittest.TestCase):
    def test_settings_text_plan_matches_clean_main_scenario(self) -> None:
        from telegram_proxy.ui import text_plan

        plan = text_plan.TELEGRAM_PROXY_SETTINGS_TEXT

        self.assertEqual(
            plan.page_subtitle,
            "Локальный прокси для Telegram. Используйте его, если Telegram подключается нестабильно.",
        )
        self.assertEqual(plan.setup_title, "Подключить Telegram")
        self.assertEqual(
            plan.setup_description,
            "Откройте ссылку. Telegram сам предложит добавить прокси.",
        )
        self.assertEqual(
            plan.setup_fallback,
            "Если Telegram не открылся, скопируйте ссылку и отправьте её себе в чат.",
        )
        self.assertEqual(plan.upstream_title, "Дополнительно")
        self.assertEqual(plan.upstream_toggle_title, "Внешний прокси")
        self.assertEqual(
            plan.upstream_toggle_description,
            "Резервный SOCKS5, если часть серверов Telegram не отвечает.",
        )

        joined = "\n".join(plan)
        self.assertNotIn("ПЕРЕЗАПУСТИТЬ", joined)
        self.assertNotIn("upstream", joined)
        self.assertNotIn("WSS relay", joined)


if __name__ == "__main__":
    unittest.main()
