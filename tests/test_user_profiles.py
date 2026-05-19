from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from core.paths import AppPaths
from profile.parser import parse_preset_text
from profile.service import ProfilePresetService
from profile.template_library import load_profile_template_library
from profile.user_profiles import create_user_profile, load_user_profile_templates
from settings.store import read_settings


class _PresetStore:
    def __init__(self, text: str = "") -> None:
        self.text = text

    def read_selected_preset_source(self, _launch_method: str):
        return self.text, SimpleNamespace(file_name="selected.txt", name="selected")

    def save_selected_preset_source(self, _launch_method: str, text: str) -> None:
        self.text = text


class UserProfilesTests(unittest.TestCase):
    def test_create_user_profile_saves_settings_and_creates_list_files(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths(user_root=root, local_root=root)
            with patch("settings.store.MAIN_DIRECTORY", str(root)):
                profile_id = create_user_profile(paths, name="Мой сайт", protocol="tcp", ports="80,443")
                settings = read_settings()

            profiles = settings["user_profiles"]["profiles"]
            self.assertIn(profile_id, profiles)
            self.assertEqual(profiles[profile_id]["name"], "Мой сайт")
            self.assertEqual(profiles[profile_id]["protocol"], "tcp")
            self.assertEqual(profiles[profile_id]["ports"], "80,443")
            self.assertTrue((root / "lists" / "moi-sait.txt").is_file())
            self.assertTrue((root / "lists" / "ipset-moi-sait.txt").is_file())

    def test_user_profile_is_loaded_as_disabled_template(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths(user_root=root, local_root=root)
            with patch("settings.store.MAIN_DIRECTORY", str(root)):
                profile_id = create_user_profile(paths, name="My Site", protocol="udp", ports="443")
                templates = load_user_profile_templates(paths, "winws2")

        profile = templates[f"user:{profile_id}"]
        self.assertEqual(profile.name, "My Site")
        self.assertIn("--filter-udp=443", profile.match.filter_lines)
        self.assertIn("--hostlist=lists/my-site.txt", profile.match.hostlist_lines)
        self.assertIn("--lua-desync=pass", [segment.text for segment in profile.segments])

    def test_winws1_user_profile_uses_first_strategy_from_protocol_catalog(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            catalog_dir = root / "profile" / "strategy_catalogs" / "winws1"
            catalog_dir.mkdir(parents=True)
            (catalog_dir / "tcp.txt").write_text(
                "\n".join(
                    (
                        "[first_tcp]",
                        "name = first tcp",
                        "--dpi-desync=fake",
                        "--dup=2",
                        "",
                        "[second_tcp]",
                        "name = second tcp",
                        "--dpi-desync=split2",
                        "",
                    )
                ),
                encoding="utf-8",
            )
            paths = AppPaths(user_root=root, local_root=root)
            with patch("settings.store.MAIN_DIRECTORY", str(root)):
                profile_id = create_user_profile(paths, name="My TCP", protocol="tcp", ports="80,443")
                templates = load_user_profile_templates(paths, "winws1")

        profile = templates[f"user:{profile_id}"]
        texts = [segment.text for segment in profile.segments]
        self.assertIn("--filter-tcp=80,443", profile.match.filter_lines)
        self.assertIn("--hostlist=lists/my-tcp.txt", profile.match.hostlist_lines)
        self.assertIn("--dpi-desync=fake", texts)
        self.assertIn("--dup=2", texts)
        self.assertNotIn("--dpi-desync=split2", texts)

    def test_list_profiles_includes_user_profile_and_enabling_adds_it_to_preset(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "profile" / "templates").mkdir(parents=True)
            (root / "profile" / "templates" / "all_profiles.txt").write_text("", encoding="utf-8")
            store = _PresetStore("")
            feature = SimpleNamespace(
                _presets_feature=store,
                _app_paths=AppPaths(user_root=root, local_root=root),
            )

            with patch("settings.store.MAIN_DIRECTORY", str(root)):
                profile_id = create_user_profile(feature._app_paths, name="My Site", protocol="tcp", ports="80,443")
                service = ProfilePresetService(feature, "zapret2_mode")
                payload = service.list_profiles()
                new_key = service.set_profile_enabled(f"template:user:{profile_id}", True)

        self.assertEqual(len(payload.items), 1)
        self.assertFalse(payload.items[0].in_preset)
        self.assertTrue(payload.items[0].key.startswith("template:user:"))
        self.assertEqual(new_key, "profile:0")
        preset = parse_preset_text(store.text, engine="winws2")
        self.assertEqual(len(preset.profiles), 1)
        self.assertIn("--filter-tcp=80,443", preset.profiles[0].match.filter_lines)
        self.assertIn("--hostlist=lists/my-site.txt", preset.profiles[0].match.hostlist_lines)
        self.assertIn("--lua-desync=pass", [segment.text for segment in preset.profiles[0].segments])

    def test_template_library_is_single_entry_for_stock_and_user_profiles(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            templates_dir = root / "profile" / "templates"
            templates_dir.mkdir(parents=True)
            (templates_dir / "all_profiles.txt").write_text(
                "\n".join(
                    (
                        "--name=Stock Site",
                        "--filter-tcp=443",
                        "--hostlist=lists/stock.txt",
                        "--lua-desync=pass",
                        "",
                    )
                ),
                encoding="utf-8",
            )
            paths = AppPaths(user_root=root, local_root=root)

            with patch("settings.store.MAIN_DIRECTORY", str(root)):
                profile_id = create_user_profile(paths, name="My Site", protocol="udp", ports="443")
                templates = load_profile_template_library(paths, "winws2")

        self.assertIn("all_profiles:0", templates)
        self.assertIn(f"user:{profile_id}", templates)
        self.assertEqual(templates["all_profiles:0"].name, "Stock Site")
        self.assertEqual(templates[f"user:{profile_id}"].name, "My Site")


if __name__ == "__main__":
    unittest.main()
