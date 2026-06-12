import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QWidget

from presets.ui.common.preset_subpage_base import PresetRawEditorPage, RawPresetRuntimeActions, _RenameDialog


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
        self.assertEqual(page.menuButton.property("screenReaderStateText"), "Открыть меню действий пресета")
        self.assertIn("переименовать", page.menuButton.accessibleDescription())
        self.assertEqual(page.activateButton.accessibleName(), "Сделать пресет активным")
        self.assertEqual(page.activateButton.property("screenReaderStateText"), "Сделать пресет активным")
        self.assertIn("выбранным для запуска", page.activateButton.accessibleDescription())
        self.assertEqual(page.openExternalButton.accessibleName(), "Открыть пресет в редакторе")
        self.assertEqual(page.openExternalButton.property("screenReaderStateText"), "Открыть пресет в редакторе")
        self.assertIn("внешнем текстовом редакторе", page.openExternalButton.accessibleDescription())
        self.assertEqual(page.runtimeToggleButton.accessibleName(), "Запустить пресет")
        self.assertEqual(page.runtimeToggleButton.property("screenReaderStateText"), "Запустить пресет")
        self.assertIn("Запускает Zapret", page.runtimeToggleButton.accessibleDescription())
        self.assertEqual(page.searchInput.accessibleName(), "Поиск по тексту пресета")
        self.assertEqual(page.searchInput.property("screenReaderStateText"), "Поиск по тексту пресета")
        self.assertIn("После ввода перейдите к тексту пресета клавишей Tab", page.searchInput.accessibleDescription())
        self.assertEqual(page.editor.accessibleName(), "Текст открытого пресета")
        self.assertEqual(page.editor.property("screenReaderStateText"), "Текст открытого пресета")

    def test_rename_dialog_is_named_for_screen_reader(self) -> None:
        parent = QWidget()
        parent.resize(640, 480)
        parent.show()
        self.addCleanup(parent.deleteLater)

        dialog = _RenameDialog("Default", [], parent)
        self.addCleanup(dialog.deleteLater)

        self.assertEqual(dialog.nameEdit.accessibleName(), "Новое название открытого пресета")
        self.assertIn("Текущее имя: Default", dialog.nameEdit.accessibleDescription())
        self.assertEqual(dialog.yesButton.accessibleName(), "Переименовать открытый пресет")
        self.assertIn("Меняет имя открытого пресета", dialog.yesButton.accessibleDescription())
        self.assertEqual(dialog.cancelButton.accessibleName(), "Отменить переименование открытого пресета")

        dialog.nameEdit.setText("")
        self.assertFalse(dialog.validate())

        self.assertEqual(dialog.warningLabel.accessibleName(), "Ошибка: Введите название.")
        self.assertEqual(dialog.warningLabel.property("screenReaderStateText"), "Ошибка: Введите название.")


if __name__ == "__main__":
    unittest.main()
