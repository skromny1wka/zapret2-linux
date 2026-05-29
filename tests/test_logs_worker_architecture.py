from __future__ import annotations

import inspect
import unittest

from app.feature_facades.logs import LogsFeature
import log.open_folder_worker as open_folder_worker
import log.support_worker as support_worker


class LogsWorkerArchitectureTests(unittest.TestCase):
    def test_logs_workers_use_commands_not_feature_object(self) -> None:
        feature_source = inspect.getsource(LogsFeature)
        worker_source = "\n".join(
            (
                inspect.getsource(open_folder_worker.LogsOpenFolderWorker),
                inspect.getsource(support_worker.LogsSupportPrepareWorker),
            )
        )

        self.assertNotIn("logs_feature=self", feature_source)
        self.assertNotIn("self._logs", worker_source)
        self.assertIn("log_commands.open_logs_folder", worker_source)
        self.assertIn("log_commands.prepare_support_bundle", worker_source)


if __name__ == "__main__":
    unittest.main()
