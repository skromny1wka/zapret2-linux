from __future__ import annotations

import importlib.util
import inspect
import unittest

import about.plans as about_plans


class AboutActionsArchitectureTests(unittest.TestCase):
    def test_about_open_actions_live_in_commands_not_plans(self) -> None:
        spec = importlib.util.find_spec("about.commands")

        self.assertIsNotNone(spec)

        import about.commands as about_commands

        plans_source = inspect.getsource(about_plans)
        commands_source = inspect.getsource(about_commands)

        self.assertNotIn("subprocess", plans_source)
        self.assertNotIn("webbrowser.open", plans_source)
        self.assertIn("open_help_folder", commands_source)
        self.assertIn("webbrowser.open", commands_source)
        self.assertIn("subprocess.Popen", commands_source)


if __name__ == "__main__":
    unittest.main()
