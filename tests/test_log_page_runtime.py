import tempfile
import unittest
from pathlib import Path

from app.feature_facades.logs import LogsFeature
from log.commands import build_tail_start_plan


class LogPageRuntimeTests(unittest.TestCase):
    def test_logs_feature_has_no_live_winws_output_api(self) -> None:
        feature = LogsFeature()

        self.assertFalse(hasattr(feature, "start_winws_output_worker"))
        self.assertFalse(hasattr(feature, "create_winws_output_worker"))
        self.assertFalse(hasattr(feature, "build_winws_output_plan"))

    def test_tail_plan_does_not_reload_unchanged_log_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "zapret_log.txt"
            log_path.write_text("line 1\nline 2\n", encoding="utf-8")

            first_plan = build_tail_start_plan(current_log_file=str(log_path))
            second_plan = build_tail_start_plan(
                current_log_file=str(log_path),
                previous_signature=first_plan.file_signature,
            )

        self.assertTrue(first_plan.should_clear_view)
        self.assertEqual(first_plan.initial_max_bytes, 1024 * 1024)
        self.assertFalse(second_plan.should_clear_view)
        self.assertEqual(second_plan.initial_max_bytes, 0)


if __name__ == "__main__":
    unittest.main()
