import inspect
import unittest

from telegram_proxy import commands as telegram_proxy_commands
from telegram_proxy import workers as telegram_proxy_workers


class TelegramProxyWorkerArchitectureTests(unittest.TestCase):
    def test_relay_reachability_probe_is_owned_by_commands(self) -> None:
        worker_source = inspect.getsource(telegram_proxy_workers.TelegramProxyRelayCheckWorker.run)

        self.assertTrue(hasattr(telegram_proxy_commands, "check_relay_reachable"))
        command_source = inspect.getsource(telegram_proxy_commands.check_relay_reachable)

        self.assertIn("telegram_proxy_commands.check_relay_reachable", worker_source)
        self.assertNotIn("telegram_proxy.wss_proxy", worker_source)
        self.assertIn("telegram_proxy.wss_proxy", command_source)
        self.assertIn("check_relay_reachable", command_source)


if __name__ == "__main__":
    unittest.main()
