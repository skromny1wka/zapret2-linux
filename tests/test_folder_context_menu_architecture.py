from __future__ import annotations

import inspect
import unittest

from ui.widgets import folder_context_menu


class FolderContextMenuArchitectureTests(unittest.TestCase):
    def test_folder_context_menu_returns_action_before_dispatch(self) -> None:
        source = inspect.getsource(folder_context_menu.show_folder_context_menu)

        self.assertIn("exec_popup_menu", source)
        self.assertIn("capture_action=True", source)
        self.assertIn("action_map", source)
        self.assertNotIn("menu.exec(", source)
        self.assertNotIn("triggered.connect(lambda: _run_folder_action", source)


if __name__ == "__main__":
    unittest.main()
