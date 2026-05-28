from __future__ import annotations

import sys
import unittest
import inspect
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))


class ServerStatusWorkerContractTests(unittest.TestCase):
    def test_background_server_check_does_not_stop_running_dpi_on_network_error(self) -> None:
        from updater import server_status_workers

        runtime_feature = SimpleNamespace(
            is_any_running=Mock(return_value=True),
            shutdown_sync=Mock(),
        )
        pool = SimpleNamespace(
            servers=[
                {
                    "id": "primary",
                    "name": "Primary",
                    "host": "example.invalid",
                    "https_port": 443,
                    "http_port": 80,
                }
            ],
            stats={},
            record_failure=Mock(),
            record_success=Mock(),
        )
        worker = server_status_workers.ServerCheckWorker(
            update_pool_stats=True,
            telegram_only=False,
        )

        with (
            patch.object(server_status_workers, "should_verify_ssl", return_value=False),
            patch.object(server_status_workers.ServerCheckWorker, "_request_versions_json", return_value=(None, "timeout", "direct")),
            patch("updater.server_pool.get_server_pool", return_value=pool),
            patch("updater.telegram_updater.is_telegram_available", return_value=False),
            patch("updater.github_release.check_rate_limit", return_value={"remaining": 1, "limit": 60}),
            patch.object(server_status_workers._time, "sleep"),
        ):
            worker.run()

        runtime_feature.shutdown_sync.assert_not_called()
        pool.record_failure.assert_called_once()

    def test_background_server_worker_has_no_runtime_shutdown_dependency(self) -> None:
        from updater import server_status_workers

        init_signature = inspect.signature(server_status_workers.ServerCheckWorker.__init__)
        worker_source = inspect.getsource(server_status_workers.ServerCheckWorker)

        self.assertNotIn("runtime_feature", init_signature.parameters)
        self.assertNotIn("shutdown_sync", worker_source)
        self.assertNotIn("is_any_running", worker_source)


if __name__ == "__main__":
    unittest.main()
