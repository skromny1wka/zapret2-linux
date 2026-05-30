from __future__ import annotations

import unittest

from ui.presets_menu.model import PresetListModel


class PresetListModelGuardTests(unittest.TestCase):
    def test_rename_preset_skips_same_file_and_name(self) -> None:
        model = PresetListModel()
        model.set_rows([
            {
                "kind": "preset",
                "file_name": "Default.txt",
                "name": "Default",
                "folder_key": "common",
            },
        ])
        self.assertFalse(model.rename_preset("Default.txt", "Default.txt", name="Default"))


if __name__ == "__main__":
    unittest.main()
