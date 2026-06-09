from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QWidget
from qfluentwidgets import BodyLabel, CaptionLabel, ComboBox, RadioButton, SegmentedWidget

from ui.fluent_widgets import SettingsCard
from ui.pages.appearance_page_top_build import (
    build_background_section,
    build_display_mode_section,
    build_language_section,
)


class AppearanceAccessibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = QApplication.instance() or QApplication([])

    def test_display_mode_selector_reads_current_mode(self) -> None:
        widgets = build_display_mode_section(
            page=None,
            tr_language="ru",
            add_section_title=lambda **_kwargs: BodyLabel("Режим отображения"),
            content_parent=QWidget(),
            settings_card_cls=SettingsCard,
            caption_label_cls=CaptionLabel,
            segmented_widget_cls=SegmentedWidget,
            on_display_mode_changed=lambda _mode: None,
        )
        self.addCleanup(widgets.card.deleteLater)

        self.assertEqual(widgets.segmented.accessibleName(), "Режим отображения интерфейса, выбрано: Тёмный")
        self.assertIn("светлый, тёмный или автоматический", widgets.segmented.accessibleDescription())

        widgets.segmented.setCurrentItem("light")

        self.assertEqual(widgets.segmented.accessibleName(), "Режим отображения интерфейса, выбрано: Светлый")
        self.assertEqual(
            widgets.segmented.property("screenReaderStateText"),
            "Режим отображения интерфейса, выбрано: Светлый",
        )

    def test_language_selector_reads_current_language(self) -> None:
        widgets = build_language_section(
            tr_language="ru",
            add_section_title=lambda **_kwargs: None,
            settings_card_cls=SettingsCard,
            caption_label_cls=CaptionLabel,
            body_label_cls=BodyLabel,
            combo_cls=ComboBox,
            on_ui_language_changed=lambda _index: None,
        )
        self.addCleanup(widgets.card.deleteLater)

        self.assertIn("Язык интерфейса", widgets.combo.accessibleName())
        self.assertIn("выбрано:", widgets.combo.accessibleName())
        self.assertIn("Выберите язык", widgets.combo.accessibleDescription())

    def test_background_controls_read_state_and_premium_limit(self) -> None:
        widgets = build_background_section(
            tr_language="ru",
            add_section_title=lambda **_kwargs: None,
            settings_card_cls=SettingsCard,
            caption_label_cls=CaptionLabel,
            body_label_cls=BodyLabel,
            radio_button_cls=RadioButton,
            combo_cls=ComboBox,
            on_bg_preset_toggled=lambda *_args: None,
            on_rkn_background_changed=lambda _index: None,
        )
        self.addCleanup(widgets.card.deleteLater)

        self.assertEqual(widgets.radio_standard.accessibleName(), "Фон окна: Стандартный, выбрано")
        self.assertEqual(widgets.radio_amoled.accessibleName(), "Фон окна: AMOLED — чёрный, недоступно без Premium")
        self.assertEqual(widgets.radio_rkn_chan.accessibleName(), "Фон окна: РКН Тян, недоступно без Premium")
        self.assertEqual(widgets.rkn_background_combo.accessibleName(), "Фон РКН Тян, вариантов пока нет")


if __name__ == "__main__":
    unittest.main()
