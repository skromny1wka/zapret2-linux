from __future__ import annotations

import inspect
import unittest

from ui.pages.base_page import BasePage


class BasePageLayoutContractTests(unittest.TestCase):
    def test_base_page_clamps_content_width_to_viewport(self) -> None:
        init = inspect.getsource(BasePage.__init__)
        sync = inspect.getsource(BasePage._sync_content_width_to_viewport)
        resize = inspect.getsource(BasePage.resizeEvent)
        show = inspect.getsource(BasePage.showEvent)

        self.assertIn("ScrollBarAlwaysOff", init)
        self.assertIn("self.content.setMinimumWidth(0)", init)
        self.assertIn("self.viewport().width()", sync)
        self.assertIn("self.content.setMaximumWidth(width)", sync)
        self.assertIn("_sync_content_width_to_viewport", resize)
        self.assertIn("_sync_content_width_to_viewport", show)

    def test_base_page_show_event_logs_internal_timing_steps(self) -> None:
        show = inspect.getsource(BasePage.showEvent)

        self.assertIn("_log_show_step_timing", show)
        self.assertIn("show.event.sync_width", show)
        self.assertIn("show.event.ready_callbacks", show)
        self.assertIn("show.event.schedule_activation", show)
        self.assertIn("show.event.theme_flush", show)


if __name__ == "__main__":
    unittest.main()
