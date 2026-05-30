from __future__ import annotations

import inspect
import unittest
from unittest.mock import Mock


class UserPresetsDependencyBoundaryTests(unittest.TestCase):
    def test_user_presets_page_receives_open_url_callable_instead_of_external_feature(self) -> None:
        from app.page_names import PageName
        from presets.ui.common.user_presets_page import UserPresetsPageBase
        from ui.page_deps.presets import build_user_presets_page_kwargs

        init_source = inspect.getsource(UserPresetsPageBase.__init__)
        page_source = inspect.getsource(UserPresetsPageBase)
        runtime_source = inspect.getsource(UserPresetsPageBase._build_page_runtime)

        self.assertIn("open_url", init_source)
        self.assertNotIn("external_actions_feature", init_source)
        self.assertNotIn("self._external_actions", page_source)
        self.assertIn("open_url=self._open_url", runtime_source)

        external_actions = Mock()
        kwargs = build_user_presets_page_kwargs(
            page_name=PageName.ZAPRET2_USER_PRESETS,
            presets_feature=Mock(),
            external_actions_feature=external_actions,
            open_preset_raw_editor=Mock(),
            ui_state_store=Mock(),
        )

        self.assertIs(kwargs["open_url"], external_actions.open_url)
        self.assertNotIn("external_actions_feature", kwargs)


if __name__ == "__main__":
    unittest.main()
