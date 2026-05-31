from __future__ import annotations

import inspect
import unittest

import telegram_proxy.actions as telegram_actions
import telegram_proxy.commands as telegram_commands


class TelegramProxyActionsArchitectureTests(unittest.TestCase):
    def test_external_open_actions_live_in_commands_not_actions(self) -> None:
        actions_source = inspect.getsource(telegram_actions)
        commands_source = inspect.getsource(telegram_commands)

        self.assertNotIn("subprocess", actions_source)
        self.assertNotIn("webbrowser.open", actions_source)
        self.assertNotIn("open_log_file", actions_source)
        self.assertNotIn("open_external_link", actions_source)

        self.assertIn("def open_log_file", commands_source)
        self.assertIn("def open_external_link", commands_source)
        self.assertIn("subprocess.Popen", commands_source)
        self.assertIn("webbrowser.open", commands_source)


if __name__ == "__main__":
    unittest.main()
