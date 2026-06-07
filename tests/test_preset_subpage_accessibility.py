import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from presets.ui.common.preset_subpage_base import PresetRawEditorPage, RawPresetRuntimeActions


class PresetSubpageAccessibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_main_controls_are_named_for_screen_reader(self) -> None:
        page = PresetRawEditorPage(
            create_raw_preset_load_worker=lambda *_args, **_kwargs: None,
            create_raw_preset_save_worker=lambda *_args, **_kwargs: None,
            create_raw_preset_activate_worker=lambda *_args, **_kwargs: None,
            create_raw_preset_action_worker=lambda *_args, **_kwargs: None,
            launch_method="zapret2",
            title="Пресет",
            open_back=lambda: None,
            open_root=lambda: None,
            runtime_actions=RawPresetRuntimeActions(
                start=lambda *_args, **_kwargs: None,
                stop=lambda *_args, **_kwargs: None,
                is_available=lambda: True,
            ),
            ui_state_store=None,
        )
        self.addCleanup(page.deleteLater)

        self.assertEqual(page.menuButton.accessibleName(), "Открыть меню действий пресета")
        self.assertIn("переименовать", page.menuButton.accessibleDescription())
        self.assertEqual(page.activateButton.accessibleName(), "Сделать пресет активным")
        self.assertIn("выбранным для запуска", page.activateButton.accessibleDescription())
        self.assertEqual(page.openExternalButton.accessibleName(), "Открыть пресет в редакторе")
        self.assertIn("внешнем текстовом редакторе", page.openExternalButton.accessibleDescription())
        self.assertEqual(page.runtimeToggleButton.accessibleName(), "Запустить пресет")
        self.assertIn("Запускает Zapret", page.runtimeToggleButton.accessibleDescription())
        self.assertEqual(page.searchInput.accessibleName(), "Поиск по тексту пресета")
        self.assertEqual(page.editor.accessibleName(), "Текст открытого пресета")


if __name__ == "__main__":
    unittest.main()
