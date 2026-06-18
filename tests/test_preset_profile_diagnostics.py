from __future__ import annotations

import inspect
import time
import unittest
from unittest.mock import patch

from app.page_names import PageName
from ui.page_host import WindowPageHost


class PresetProfileDiagnosticsTests(unittest.TestCase):
    def test_page_host_switch_metric_includes_target_page_details(self) -> None:
        class _FakePage:
            def __init__(self, name: str, children: int, visible: int) -> None:
                self._name = name
                self._children = children
                self._visible = visible

            def objectName(self):  # noqa: N802
                return self._name

            def findChildren(self, _kind):
                children = []
                for index in range(self._children):
                    visible = index < self._visible
                    children.append(type("Child", (), {"isVisible": lambda _self, visible=visible: visible})())
                return children

        class _FakeStack:
            def __init__(self) -> None:
                self.isAnimationEnabled = True
                self.updates_enabled = True
                self.current = _FakePage("oldPage", 1, 1)

            def count(self) -> int:
                return 2

            def currentWidget(self):  # noqa: N802
                return self.current

            def setUpdatesEnabled(self, enabled):  # noqa: N802
                self.updates_enabled = bool(enabled)

            def updatesEnabled(self):  # noqa: N802
                return self.updates_enabled

            def setCurrentWidget(self, page, need_pop_out=False):  # noqa: N802
                _ = need_pop_out
                time.sleep(0.02)
                self.current = page

        stack = _FakeStack()
        host = WindowPageHost(window=type("Window", (), {"stackedWidget": stack})(), page_factory=None)
        page = _FakePage("newPage", 7, 3)
        events: list[tuple[str, str]] = []

        with patch(
            "ui.page_host.log_page_timing",
            side_effect=lambda _page, stage, *_args, **kwargs: events.append((stage, str(kwargs.get("extra") or ""))),
        ):
            self.assertTrue(
                host.set_stacked_widget_current_page(
                    page,
                    animate=False,
                    page_name=PageName.ZAPRET2_USER_PRESETS,
                )
            )

        set_current_extra = next(extra for stage, extra in events if stage == "open.switch.set_current")
        self.assertIn("from=oldPage", set_current_extra)
        self.assertIn("to=newPage", set_current_extra)
        self.assertIn("children=7", set_current_extra)
        self.assertIn("visible=3", set_current_extra)
        self.assertIn("stack=2", set_current_extra)

    def test_profile_list_visible_timing_includes_internal_steps(self) -> None:
        from profile import service

        timing_source = inspect.getsource(service.ProfilePresetService._log_timing)

        self.assertIn("log_ui_timing_since", timing_source)
        self.assertIn('"feature"', timing_source)
        self.assertIn('"profile"', timing_source)
        self.assertIn("important=True", timing_source)

    def test_user_presets_metadata_read_is_visible_timing(self) -> None:
        import presets.user_presets_runtime_service as runtime_service

        timing_source = inspect.getsource(runtime_service._log_user_presets_timing)
        worker_source = inspect.getsource(runtime_service.UserPresetsMetadataLoadWorker.run)
        self.assertIn("log_ui_timing_since", timing_source)
        self.assertIn('"feature"', timing_source)
        self.assertIn('"user_presets"', timing_source)
        self.assertIn("_log_user_presets_timing", worker_source)
        self.assertIn("user_presets.metadata.read", worker_source)


if __name__ == "__main__":
    unittest.main()
