from __future__ import annotations

import inspect
import unittest


class OrchestraWorkerArchitectureTests(unittest.TestCase):
    def test_page_workers_receive_action_functions(self) -> None:
        from orchestra.page_workers import OrchestraClearLearnedWorker, OrchestraLogHistoryLoadWorker

        clear_init = inspect.getsource(OrchestraClearLearnedWorker.__init__)
        clear_run = inspect.getsource(OrchestraClearLearnedWorker.run)
        history_init = inspect.getsource(OrchestraLogHistoryLoadWorker.__init__)
        history_run = inspect.getsource(OrchestraLogHistoryLoadWorker.run)

        self.assertIn("clear_learned_data", clear_init)
        self.assertIn("self._clear_learned_data", clear_init)
        self.assertNotIn("self._controller", clear_init)
        self.assertIn("self._clear_learned_data()", clear_run)
        self.assertNotIn("self._controller.clear_learned_data", clear_run)

        self.assertIn("load_log_history", history_init)
        self.assertIn("self._load_log_history", history_init)
        self.assertNotIn("self._controller", history_init)
        self.assertIn("self._load_log_history()", history_run)
        self.assertNotIn("self._controller.load_log_history", history_run)

    def test_ratings_worker_receives_loader_function(self) -> None:
        from orchestra.ratings_worker import OrchestraRatingsStateLoadWorker

        init_source = inspect.getsource(OrchestraRatingsStateLoadWorker.__init__)
        run_source = inspect.getsource(OrchestraRatingsStateLoadWorker.run)

        self.assertIn("load_state", init_source)
        self.assertIn("self._load_state", init_source)
        self.assertNotIn("self._controller", init_source)
        self.assertIn("self._load_state()", run_source)
        self.assertNotIn("self._controller.load_state", run_source)

    def test_managed_workers_receive_action_functions(self) -> None:
        from orchestra.managed_lists_workers import (
            OrchestraManagedActionWorker,
            OrchestraManagedSnapshotLoadWorker,
        )

        snapshot_init = inspect.getsource(OrchestraManagedSnapshotLoadWorker.__init__)
        snapshot_run = inspect.getsource(OrchestraManagedSnapshotLoadWorker.run)
        action_init = inspect.getsource(OrchestraManagedActionWorker.__init__)
        action_run = inspect.getsource(OrchestraManagedActionWorker.run)

        self.assertIn("load_snapshot", snapshot_init)
        self.assertIn("self._load_snapshot", snapshot_init)
        self.assertNotIn("self._controller", snapshot_init)
        self.assertIn("self._load_snapshot()", snapshot_run)
        self.assertNotIn("self._controller.reload_snapshot", snapshot_run)

        for name in (
            "change_strategy",
            "remove_strategy",
            "add_strategy",
            "clear_user_strategies",
            "is_blocked_strategy",
            "current_strategy",
            "clear_strategies",
            "load_snapshot",
        ):
            self.assertIn(name, action_init)
        self.assertNotIn("self._controller", action_init)
        self.assertNotIn("self._controller.", action_run)

    def test_whitelist_workers_receive_action_functions(self) -> None:
        from orchestra.managed_lists_workers import (
            OrchestraWhitelistActionWorker,
            OrchestraWhitelistSnapshotLoadWorker,
        )

        snapshot_init = inspect.getsource(OrchestraWhitelistSnapshotLoadWorker.__init__)
        snapshot_run = inspect.getsource(OrchestraWhitelistSnapshotLoadWorker.run)
        action_init = inspect.getsource(OrchestraWhitelistActionWorker.__init__)
        action_run = inspect.getsource(OrchestraWhitelistActionWorker.run)

        self.assertIn("load_snapshot", snapshot_init)
        self.assertIn("self._load_snapshot", snapshot_init)
        self.assertNotIn("self._controller", snapshot_init)
        self.assertIn("self._load_snapshot(refresh=self._refresh)", snapshot_run)
        self.assertNotIn("self._controller.snapshot", snapshot_run)

        for name in ("add_domain", "remove_domain", "clear_user_domains", "load_snapshot"):
            self.assertIn(name, action_init)
        self.assertNotIn("self._controller", action_init)
        self.assertNotIn("self._controller.", action_run)


if __name__ == "__main__":
    unittest.main()
