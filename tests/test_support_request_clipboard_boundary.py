from __future__ import annotations

import inspect
import unittest
from unittest.mock import patch

import support_request_bundle


class SupportRequestClipboardBoundaryTests(unittest.TestCase):
    def test_support_request_bundle_does_not_use_qt_clipboard(self) -> None:
        source = inspect.getsource(support_request_bundle)

        self.assertNotIn("QApplication", source)
        self.assertNotIn("PyQt6", source)

    def test_prepare_support_request_uses_local_clipboard_helper(self) -> None:
        with patch.object(support_request_bundle, "_copy_to_clipboard", return_value=True) as copy:
            result = support_request_bundle.prepare_support_request(
                bundle_prefix="support",
                context_label="Test",
                candidate_paths=[],
                open_discussions=False,
                open_bundle_folder=False,
            )

        copy.assert_called_once_with(result.template_text)
        self.assertTrue(result.copied_to_clipboard)


if __name__ == "__main__":
    unittest.main()
