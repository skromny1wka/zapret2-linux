from __future__ import annotations

import importlib
import inspect
import unittest

import telegram_proxy.actions as telegram_actions
import telegram_proxy.commands as telegram_commands
import telegram_proxy.manager as telegram_manager


class TelegramProxyActionsArchitectureTests(unittest.TestCase):
    def test_external_open_actions_live_in_commands_not_actions(self) -> None:
        actions_source = inspect.getsource(telegram_actions)
        commands_source = inspect.getsource(telegram_commands)

        self.assertNotIn("subprocess", actions_source)
        self.assertNotIn("webbrowser.open", actions_source)
        self.assertNotIn("open_log_file", actions_source)
        self.assertNotIn("open_external_link", actions_source)

        self.assertIn("def open_log_file", commands_source)
        self.assertIn("def open_external_link", commands_source)
        self.assertIn("subprocess.Popen", commands_source)
        self.assertIn("webbrowser.open", commands_source)

    def test_upstream_config_builder_has_single_settings_owner(self) -> None:
        manager_source = inspect.getsource(telegram_manager.build_upstream_proxy_config_from_settings)
        commands_source = inspect.getsource(telegram_commands.build_upstream_config)

        self.assertIn("telegram_proxy.settings", manager_source)
        self.assertIn("build_upstream_config", manager_source)
        self.assertNotIn("get_tg_proxy_upstream_enabled", manager_source)
        self.assertNotIn("get_tg_proxy_upstream_host", manager_source)
        self.assertIn("telegram_proxy.settings", commands_source)

    def test_wss_proxy_is_split_into_focused_modules(self) -> None:
        raw_websocket = importlib.import_module("telegram_proxy.raw_websocket")
        routing = importlib.import_module("telegram_proxy.routing")
        relay = importlib.import_module("telegram_proxy.relay")
        stats = importlib.import_module("telegram_proxy.stats")
        wss_proxy = importlib.import_module("telegram_proxy.wss_proxy")

        self.assertIs(wss_proxy.RawWebSocket, raw_websocket.RawWebSocket)
        self.assertIs(wss_proxy.WsHandshakeError, raw_websocket.WsHandshakeError)
        self.assertIs(wss_proxy.UpstreamProxyConfig, routing.UpstreamProxyConfig)
        self.assertIs(wss_proxy.check_relay_reachable, routing.check_relay_reachable)
        self.assertIs(wss_proxy.RELAY_BUFFER, relay.RELAY_BUFFER)
        self.assertIs(wss_proxy.ProxyStats, stats.ProxyStats)

        wss_source = inspect.getsource(wss_proxy)
        self.assertIn("relay_tcp(", wss_source)
        self.assertIn("relay_wss(", wss_source)
        self.assertIn("should_route_upstream(", wss_source)


if __name__ == "__main__":
    unittest.main()
