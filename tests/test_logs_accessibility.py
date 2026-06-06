from __future__ import annotations

import inspect
import unittest

import log.ui.logs_build as logs_build
import log.ui.page as logs_page
import log.ui.runtime_helpers as runtime_helpers


class _FakeLabel:
    def __init__(self) -> None:
        self.text = ""
        self.style = ""
        self.accessible_name = ""
        self.properties = {}

    def setText(self, text: str) -> None:  # noqa: N802
        self.text = text

    def setStyleSheet(self, style: str) -> None:  # noqa: N802
        self.style = style

    def accessibleName(self) -> str:  # noqa: N802
        return self.accessible_name

    def setAccessibleName(self, text: str) -> None:  # noqa: N802
        self.accessible_name = text

    def setProperty(self, name: str, value: object) -> None:  # noqa: N802
        self.properties[name] = value


class LogsAccessibilityTests(unittest.TestCase):
    def test_logs_build_assigns_screen_reader_names_to_core_controls(self) -> None:
        source = inspect.getsource(logs_build.build_logs_primary_tab_ui)
        secondary_source = inspect.getsource(logs_build.build_logs_secondary_panels_ui)

        self.assertIn("set_control_accessibility", source)
        self.assertIn("log_combo,", source)
        self.assertIn("refresh_btn,", source)
        self.assertIn("log_text,", source)
        self.assertIn("stats_label,", source)
        self.assertIn("set_control_accessibility", secondary_source)
        self.assertIn("clear_errors_btn,", secondary_source)
        self.assertIn("errors_text,", secondary_source)

    def test_log_page_routes_info_text_through_screen_reader_state(self) -> None:
        source = inspect.getsource(logs_page.LogsPage)

        self.assertIn("def _set_info_text", source)
        self.assertIn("set_info_text_fn=self._set_info_text", source)
        self.assertIn("self._set_info_text(", source)

    def test_send_status_label_updates_screen_reader_state(self) -> None:
        label = _FakeLabel()

        runtime_helpers.render_send_status_label(
            label=label,
            text="Архив поддержки готов",
            tone="neutral",
            theme_tokens=type("Tokens", (), {"accent_hex": "#0078d4", "is_light": True})(),
        )

        self.assertEqual(label.text, "Архив поддержки готов")
        self.assertEqual(label.accessible_name, "Архив поддержки готов")
        self.assertEqual(label.properties["screenReaderStateText"], "Архив поддержки готов")

    def test_error_count_updates_screen_reader_state(self) -> None:
        errors_text = type("ErrorsText", (), {"append": lambda self, text: None})()
        label = _FakeLabel()

        count = runtime_helpers.append_error(
            errors_text=errors_text,
            errors_count_label=label,
            tr_fn=lambda _key, default: default,
            current_count=0,
            text="RuntimeError: failed",
        )

        self.assertEqual(count, 1)
        self.assertEqual(label.accessible_name, "Ошибок: 1")
        self.assertEqual(label.properties["screenReaderStateText"], "Ошибок: 1")


if __name__ == "__main__":
    unittest.main()
