from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from app.feature_facades.presets import PresetsFeature
from presets.ui.common.user_presets_page import UserPresetsPageBase
from presets.ui.common.preset_subpage_base import PresetRawEditorPage


class UserPresetActivationGuardTests(unittest.TestCase):
    def test_clicking_active_preset_does_not_start_activation_worker(self) -> None:
        page = UserPresetsPageBase.__new__(UserPresetsPageBase)
        page._runtime_service = Mock()
        page._runtime_service.active_preset_file_name.return_value = "Default.txt"
        page._runtime_service.apply_active_preset_marker_for_file = Mock()
        page._resolve_display_name = Mock()
        page._request_preset_activation = Mock()

        self.assertTrue(UserPresetsPageBase._on_activate_preset(page, "Default.txt"))

        page._runtime_service.apply_active_preset_marker_for_file.assert_not_called()
        page._resolve_display_name.assert_not_called()
        page._request_preset_activation.assert_not_called()

    def test_clicking_active_raw_preset_without_changes_does_not_start_activation_worker(self) -> None:
        page = PresetRawEditorPage.__new__(PresetRawEditorPage)
        page._run_after_raw_preset_save = Mock(return_value=True)
        page._preset_file_name = "Default.txt"
        page._preset_name = "Default"
        page._is_current_selected_file = Mock(return_value=True)
        page._set_footer = Mock()
        page._request_preset_activation = Mock()
        page._show_error = Mock()

        PresetRawEditorPage._activate_preset(page)

        page._set_footer.assert_not_called()
        page._request_preset_activation.assert_not_called()
        page._show_error.assert_not_called()

    def test_feature_worker_skips_duplicate_selected_preset_activation(self) -> None:
        feature = PresetsFeature()

        with (
            patch.object(PresetsFeature, "get_selected_source_preset_file_name", return_value="Default.txt"),
            patch.object(PresetsFeature, "activate_preset_file") as activate_preset_file,
        ):
            worker = feature.create_preset_activate_worker(
                1,
                launch_method="zapret2_mode",
                file_name="default.TXT",
                display_name="Default",
                activate_error_level="error",
                activate_error_mode="friendly",
            )
            result = worker._activate_preset(file_name="default.TXT", display_name="Default")

        activate_preset_file.assert_not_called()
        self.assertTrue(result.ok)
        self.assertEqual(result.activated_file_name, "Default.txt")

    def test_feature_worker_still_activates_when_duplicate_guard_cannot_read_selection(self) -> None:
        feature = PresetsFeature()

        with (
            patch.object(PresetsFeature, "get_selected_source_preset_file_name", side_effect=RuntimeError("settings busy")),
            patch.object(PresetsFeature, "activate_preset_file") as activate_preset_file,
        ):
            worker = feature.create_preset_activate_worker(
                1,
                launch_method="zapret2_mode",
                file_name="Other.txt",
                display_name="Other",
                activate_error_level="error",
                activate_error_mode="friendly",
            )
            result = worker._activate_preset(file_name="Other.txt", display_name="Other")

        activate_preset_file.assert_called_once_with("zapret2_mode", "Other.txt")
        self.assertTrue(result.ok)


if __name__ == "__main__":
    unittest.main()
