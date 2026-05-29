from __future__ import annotations

import inspect
import unittest

from app.feature_facades.blockcheck import BlockcheckFeature
import blockcheck.workers as blockcheck_workers


class BlockcheckWorkerArchitectureTests(unittest.TestCase):
    def test_scan_resume_and_finalize_workers_use_public_commands_not_feature_object(self) -> None:
        feature_source = "\n".join(
            (
                inspect.getsource(BlockcheckFeature.create_strategy_scan_resume_save_worker),
                inspect.getsource(BlockcheckFeature.create_strategy_scan_finalize_worker),
            )
        )
        worker_source = "\n".join(
            (
                inspect.getsource(blockcheck_workers.StrategyScanResumeSaveWorker),
                inspect.getsource(blockcheck_workers.StrategyScanFinalizeWorker),
            )
        )

        self.assertNotIn("blockcheck_feature=self", feature_source)
        self.assertNotIn("self._blockcheck", worker_source)
        self.assertIn("blockcheck_public.save_resume_state", worker_source)
        self.assertIn("blockcheck_public.finalize_scan_report", worker_source)


if __name__ == "__main__":
    unittest.main()
