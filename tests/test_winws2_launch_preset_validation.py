from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))


class Winws2LaunchPresetValidationTests(unittest.TestCase):
    def test_launch_preparation_keeps_valid_preset_text_unchanged(self) -> None:
        from winws_runtime.preset_launch_text import prepare_winws2_preset_text_for_launch

        source = "\n".join(
            (
                "--wf-tcp-out=443",
                "--filter-tcp=443",
                "--hostlist=lists/youtube.txt",
                "--payload=tls_client_hello",
                "--lua-desync=fake:blob=tls_google",
                "",
            )
        )

        prepared = prepare_winws2_preset_text_for_launch(source, source_name="valid.txt")

        self.assertEqual(prepared.text, source)
        self.assertFalse(prepared.changed)
        self.assertNotIn("--out-range=-d8", prepared.text)

    def test_launch_preparation_allows_unknown_filename_when_syntax_is_valid(self) -> None:
        from winws_runtime.preset_launch_text import prepare_winws2_preset_text_for_launch

        source = "\n".join(
            (
                "--wf-tcp-out=443",
                "--filter-tcp=443",
                "--hostlist=unknown.txt",
                "--lua-desync=fake:blob=tls_google",
                "",
            )
        )

        prepared = prepare_winws2_preset_text_for_launch(source, source_name="placeholder.txt")

        self.assertEqual(prepared.text, source)

    def test_runner_checks_unknown_filename_by_file_existence(self) -> None:
        from winws_runtime.runners.zapret2_runner import Winws2StrategyRunner

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lists_dir = root / "lists"
            lists_dir.mkdir()
            runner = object.__new__(Winws2StrategyRunner)
            runner.work_dir = str(root)
            runner.lists_dir = str(lists_dir)
            runner.bin_dir = str(root / "bin")

            source = "\n".join(
                (
                    "--wf-tcp-out=443",
                    "--filter-tcp=443",
                    "--hostlist=unknown.txt",
                    "--lua-desync=fake:blob=tls_google",
                    "",
                )
            )

            missing = runner._collect_missing_preset_references_from_text(source)
            self.assertEqual(len(missing), 1)
            self.assertIn("--hostlist=unknown.txt", missing[0][0])

            (lists_dir / "unknown.txt").write_text("example.com\n", encoding="utf-8")

            self.assertEqual(runner._collect_missing_preset_references_from_text(source), [])

    def test_launch_preparation_rejects_invalid_ranges_and_payload(self) -> None:
        from winws_runtime.preset_launch_text import prepare_winws2_preset_text_for_launch

        cases = (
            ("--out-range=8", "out-range"),
            ("--in-range=bad", "in-range"),
            ("--payload=not_a_payload", "payload"),
        )

        for line, expected in cases:
            with self.subTest(line=line):
                source = "\n".join(
                    (
                        "--wf-tcp-out=443",
                        "--filter-tcp=443",
                        "--hostlist=lists/youtube.txt",
                        line,
                        "--lua-desync=fake:blob=tls_google",
                        "",
                    )
                )
                with self.assertRaisesRegex(ValueError, expected):
                    prepare_winws2_preset_text_for_launch(source, source_name="bad.txt")

    def test_profile_editor_rejects_non_engine_range_value(self) -> None:
        from profile.parser import parse_preset_text
        from profile.winws2_editable_settings import Winws2EditableSettings, with_winws2_editable_settings
        from settings.mode import ENGINE_WINWS2

        preset = parse_preset_text(
            "\n".join(
                (
                    "--filter-tcp=443",
                    "--hostlist=lists/youtube.txt",
                    "--lua-desync=fake:blob=tls_google",
                    "",
                )
            ),
            engine=ENGINE_WINWS2,
            source_name="editable.txt",
        )

        with self.assertRaisesRegex(ValueError, "packet range"):
            with_winws2_editable_settings(
                preset,
                0,
                Winws2EditableSettings(
                    filter_kind="hostlist",
                    filter_value="lists/youtube.txt",
                    in_range="x",
                    out_range="d8",
                ),
            )


if __name__ == "__main__":
    unittest.main()
