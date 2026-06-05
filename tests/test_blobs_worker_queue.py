from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from blobs.ui.page import BlobsPage


class _FakeLabel:
    def __init__(self, _text: str = "") -> None:
        self.setProperty = Mock()


class BlobsWorkerQueueTests(unittest.TestCase):
    def test_blob_callbacks_ignored_when_new_work_is_pending(self) -> None:
        page = BlobsPage.__new__(BlobsPage)
        page._cleanup_in_progress = False
        page._ui_language = "ru"
        page._tr = lambda _key, default, **kwargs: default.format(**kwargs) if kwargs else default
        page.window = Mock(return_value=None)
        page._apply_page_theme = Mock()
        page.blobs_layout = Mock()
        page.count_label = Mock()

        page._blobs_load_pending = True
        page._blobs_load_runtime = Mock()
        page._blobs_load_runtime.is_current.return_value = True

        page._blob_action_pending = [{"action": "delete", "name": "Next"}]
        page._blob_action_runtime = Mock()
        page._blob_action_runtime.is_current.return_value = True
        page._request_blobs_load = Mock()

        page._blob_open_action_pending = ["blobs_json"]
        page._blob_open_action_runtime = Mock()
        page._blob_open_action_runtime.is_current.return_value = True

        with (
            patch("blobs.ui.page.load_blobs_into_ui") as load_blobs_into_ui,
            patch("blobs.ui.page.QLabel", _FakeLabel),
            patch("blobs.ui.runtime_helpers.clear_blobs_layout"),
            patch("blobs.ui.page.InfoBar.warning") as warning,
            patch("blobs.ui.page.log") as log_mock,
        ):
            BlobsPage._on_blobs_loaded(page, 1, {"system": [], "user": []}, True)
            BlobsPage._on_blobs_load_failed(page, 1, "old load", True)
            BlobsPage._on_blob_action_finished(page, 2, "save", True, {"name": "Old"})
            BlobsPage._on_blob_action_failed(page, 2, "delete", "old action", {"name": "Old"})
            BlobsPage._on_blob_open_action_failed(page, 3, "bin_folder", "old open")

        load_blobs_into_ui.assert_not_called()
        warning.assert_not_called()
        log_mock.assert_not_called()
        page._request_blobs_load.assert_not_called()


if __name__ == "__main__":
    unittest.main()
