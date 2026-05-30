from __future__ import annotations

import unittest
from unittest.mock import Mock

from presets.ui.common.user_presets_page import UserPresetsPageBase
from presets.ui.common.preset_subpage_base import PresetRawEditorPage
from presets.ui.common.user_presets_page_runtime import (
    UserPresetsPageRuntime,
    UserPresetsPageRuntimeConfig,
    UserPresetsRuntimeActions,
)


def _make_runtime(actions: UserPresetsRuntimeActions) -> UserPresetsPageRuntime:
    return UserPresetsPageRuntime(
        UserPresetsPageRuntimeConfig(
            launch_method="zapret2_mode",
            folder_scope="zapret2",
            empty_not_found_key="",
            empty_none_key="",
            list_log_prefix="",
            activate_error_level="error",
            activate_error_mode="friendly",
            preset_runtime_actions=actions,
            open_url=Mock(),
        )
    )


def _make_runtime_actions(**overrides) -> UserPresetsRuntimeActions:
    values = {
        "create_preset": Mock(),
        "rename_preset_by_file_name": Mock(),
        "is_selected_preset_file_name": Mock(),
        "import_preset_from_file": Mock(),
        "reset_all_presets_to_builtin": Mock(),
        "get_selected_source_preset_file_name": Mock(),
        "duplicate_preset_by_file_name": Mock(),
        "reset_preset_to_builtin_by_file_name": Mock(),
        "delete_preset_by_file_name": Mock(),
        "export_preset_plain_text": Mock(),
        "get_preset_manifest_by_file_name": Mock(),
        "list_preset_manifests": Mock(),
        "get_selected_source_preset_manifest": Mock(),
        "get_user_presets_dir": Mock(),
        "get_cached_preset_list_metadata": Mock(),
        "warm_preset_list_metadata_cache": Mock(),
        "get_preset_source_path_by_file_name": Mock(),
        "activate_preset_file": Mock(),
    }
    values.update(overrides)
    return UserPresetsRuntimeActions(**values)


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

    def test_runtime_skips_duplicate_selected_preset_activation(self) -> None:
        actions = _make_runtime_actions(
            get_selected_source_preset_file_name=Mock(return_value="Default.txt"),
        )
        runtime = _make_runtime(actions)

        result = runtime.activate_preset(file_name="default.TXT", display_name="Default")

        actions.activate_preset_file.assert_not_called()
        self.assertTrue(result.ok)
        self.assertEqual(result.activated_file_name, "Default.txt")

    def test_runtime_still_activates_when_duplicate_guard_cannot_read_selection(self) -> None:
        actions = _make_runtime_actions(
            get_selected_source_preset_file_name=Mock(side_effect=RuntimeError("settings busy")),
        )
        runtime = _make_runtime(actions)

        result = runtime.activate_preset(file_name="Other.txt", display_name="Other")

        actions.activate_preset_file.assert_called_once_with("zapret2_mode", "Other.txt")
        self.assertTrue(result.ok)


if __name__ == "__main__":
    unittest.main()
