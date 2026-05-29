from __future__ import annotations

import inspect
import unittest

from app.feature_facades.program_settings import ProgramSettingsFeature
import program_settings.public as program_settings_public
import program_settings.workers as program_settings_workers


class ProgramSettingsWorkerArchitectureTests(unittest.TestCase):
    def test_load_worker_uses_commands_not_feature_object(self) -> None:
        feature_source = inspect.getsource(ProgramSettingsFeature)
        worker_source = inspect.getsource(program_settings_workers.ProgramSettingsLoadWorker)

        self.assertNotIn("program_settings_feature=self", feature_source)
        self.assertNotIn("self._program_settings", worker_source)
        self.assertIn("program_settings_commands.load_program_settings_snapshot", worker_source)
        self.assertIn(
            "load_program_settings_snapshot",
            inspect.getsource(program_settings_public.load_program_settings_snapshot),
        )

    def test_admin_check_worker_uses_commands_not_feature_object(self) -> None:
        feature_source = inspect.getsource(ProgramSettingsFeature)
        worker_source = inspect.getsource(program_settings_workers.ProgramSettingsAdminCheckWorker)

        self.assertNotIn("program_settings_feature=self", feature_source)
        self.assertNotIn("self._program_settings", worker_source)
        self.assertIn("program_settings_commands.is_user_admin", worker_source)
        self.assertIn("is_user_admin", inspect.getsource(program_settings_public.is_user_admin))


if __name__ == "__main__":
    unittest.main()
