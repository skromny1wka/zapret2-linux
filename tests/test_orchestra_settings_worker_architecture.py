from __future__ import annotations

import inspect
import unittest

from app.feature_facades.orchestra import OrchestraFeature
import orchestra.commands as orchestra_commands
import orchestra.settings_worker as settings_worker


class OrchestraSettingsWorkerArchitectureTests(unittest.TestCase):
    def test_setting_save_worker_uses_commands_not_feature_object(self) -> None:
        feature_source = inspect.getsource(OrchestraFeature.create_setting_save_worker)
        worker_source = inspect.getsource(settings_worker.OrchestraSettingSaveWorker)

        self.assertNotIn("OrchestraSettingSaveWorker(\n            request_id,\n            self,", feature_source)
        self.assertNotIn("self._orchestra", worker_source)
        self.assertIn("runner=self.runner", feature_source)
        self.assertIn("orchestra_commands.set_setting", worker_source)
        self.assertIn("set_orchestra_setting", inspect.getsource(orchestra_commands.set_setting))


if __name__ == "__main__":
    unittest.main()
