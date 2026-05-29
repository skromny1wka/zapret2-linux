from __future__ import annotations

import unittest
from unittest.mock import Mock

from presets.ui.common.user_presets_page import UserPresetsPageBase


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


if __name__ == "__main__":
    unittest.main()
