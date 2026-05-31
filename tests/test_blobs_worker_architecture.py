from __future__ import annotations

import inspect
import unittest

from app.feature_facades.blobs import build_blobs_feature
from blobs.ui.page import BlobsPage
import blobs.workers as blobs_workers


class BlobsWorkerArchitectureTests(unittest.TestCase):
    def test_blobs_feature_does_not_expose_heavy_direct_actions(self) -> None:
        feature = build_blobs_feature()

        for attr_name in (
            "get_blobs_info",
            "save_user_blob",
            "delete_user_blob",
            "reload_blobs",
            "open_bin_folder",
            "open_blobs_json",
        ):
            self.assertFalse(hasattr(feature, attr_name), attr_name)

    def test_blobs_workers_receive_commands_from_feature(self) -> None:
        feature_source = inspect.getsource(build_blobs_feature)
        worker_source = "\n".join(
            (
                inspect.getsource(blobs_workers.BlobsLoadWorker),
                inspect.getsource(blobs_workers.BlobActionWorker),
                inspect.getsource(blobs_workers.BlobOpenActionWorker),
            )
        )

        self.assertNotIn("blobs_feature=feature", feature_source)
        self.assertNotIn("self._blobs", worker_source)
        self.assertNotIn("import blobs.public", worker_source)
        self.assertIn("get_blobs_info=", feature_source)
        self.assertIn("reload_blobs=", feature_source)
        self.assertIn("save_user_blob=", feature_source)
        self.assertIn("delete_user_blob=", feature_source)
        self.assertIn("open_bin_folder=", feature_source)
        self.assertIn("open_blobs_json=", feature_source)
        self.assertIn("self._get_blobs_info", worker_source)
        self.assertIn("self._reload_blobs", worker_source)
        self.assertIn("self._save_user_blob", worker_source)
        self.assertIn("self._delete_user_blob", worker_source)
        self.assertIn("self._open_bin_folder", worker_source)
        self.assertIn("self._open_blobs_json", worker_source)

    def test_blobs_page_uses_one_shot_runtime_for_workers(self) -> None:
        page_source = inspect.getsource(BlobsPage)
        load_source = inspect.getsource(BlobsPage._start_blobs_load_worker)
        action_source = inspect.getsource(BlobsPage._start_blob_action_worker)
        open_source = inspect.getsource(BlobsPage._start_blob_open_action_worker)
        cleanup_source = inspect.getsource(BlobsPage.cleanup)

        self.assertIn("OneShotWorkerRuntime", page_source)
        self.assertIn("_blobs_load_runtime", page_source)
        self.assertIn("_blob_action_runtime", page_source)
        self.assertIn("_blob_open_action_runtime", page_source)
        for source in (load_source, action_source, open_source):
            self.assertIn("start_qthread_worker", source)
            self.assertNotIn("worker.start()", source)
        self.assertIn("_blobs_load_runtime.stop", cleanup_source)
        self.assertIn("_blob_action_runtime.stop", cleanup_source)
        self.assertIn("_blob_open_action_runtime.stop", cleanup_source)


if __name__ == "__main__":
    unittest.main()
