from __future__ import annotations

import ctypes
import importlib
import sys
import types
import unittest


class _FakeIphlpapi:
    def __init__(self) -> None:
        self.set_calls = []
        self.get_name_server = "9.9.9.9,149.112.112.112"

    def SetInterfaceDnsSettings(self, interface_guid, settings_ptr):  # noqa: N802
        settings = getattr(settings_ptr, "_obj", None)
        if settings is None:
            settings = settings_ptr.contents
        self.set_calls.append((interface_guid, settings))
        return 0

    def GetInterfaceDnsSettings(self, interface_guid, settings_ptr):  # noqa: N802
        _ = interface_guid
        settings = getattr(settings_ptr, "_obj", None)
        if settings is None:
            settings = settings_ptr.contents
        settings.NameServer = self.get_name_server
        return 0

    def FreeInterfaceDnsSettings(self, settings_ptr):  # noqa: N802
        _ = settings_ptr


class DnsCoreWinApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self._old_windll = getattr(ctypes, "windll", None)
        self._old_winreg = sys.modules.get("winreg")
        self.iphlpapi = _FakeIphlpapi()
        ctypes.windll = types.SimpleNamespace(
            iphlpapi=self.iphlpapi,
            user32=types.SimpleNamespace(SendNotifyMessageW=lambda *_args: True),
            dnsapi=types.SimpleNamespace(DnsFlushResolverCache=lambda: True),
        )
        sys.modules["winreg"] = types.SimpleNamespace()
        sys.modules.pop("dns.dns_core", None)
        self.dns_core = importlib.import_module("dns.dns_core")

    def tearDown(self) -> None:
        sys.modules.pop("dns.dns_core", None)
        if self._old_windll is None:
            delattr(ctypes, "windll")
        else:
            ctypes.windll = self._old_windll
        if self._old_winreg is None:
            sys.modules.pop("winreg", None)
        else:
            sys.modules["winreg"] = self._old_winreg

    def _manager(self):
        manager = self.dns_core.DNSManager()
        manager.get_adapter_guid = lambda _adapter_name: "{C78087CA-DCB3-4993-B9D1-7CC33D0A288B}"
        return manager

    def test_custom_ipv4_dns_uses_interface_dns_settings_in_order(self) -> None:
        ok, message = self._manager().set_custom_dns(
            "Ethernet",
            "10.10.10.10",
            "10.10.10.11",
            "IPv4",
        )

        self.assertTrue(ok, message)
        self.assertEqual(1, len(self.iphlpapi.set_calls))
        _guid, settings = self.iphlpapi.set_calls[0]
        self.assertEqual(self.dns_core.DNS_INTERFACE_SETTINGS_VERSION1, settings.Version)
        self.assertEqual(self.dns_core.DNS_SETTING_NAMESERVER, settings.Flags)
        self.assertEqual("10.10.10.10,10.10.10.11", settings.NameServer)

    def test_auto_dns_clears_ipv4_name_server_through_interface_settings(self) -> None:
        ok, message = self._manager().set_auto_dns("Ethernet", "IPv4")

        self.assertTrue(ok, message)
        self.assertEqual(1, len(self.iphlpapi.set_calls))
        _guid, settings = self.iphlpapi.set_calls[0]
        self.assertEqual(self.dns_core.DNS_SETTING_NAMESERVER, settings.Flags)
        self.assertEqual("", settings.NameServer)

    def test_custom_ipv6_dns_sets_ipv6_flag(self) -> None:
        ok, message = self._manager().set_custom_dns(
            "Ethernet",
            "2620:fe::fe",
            "2620:fe::9",
            "IPv6",
        )

        self.assertTrue(ok, message)
        self.assertEqual(1, len(self.iphlpapi.set_calls))
        _guid, settings = self.iphlpapi.set_calls[0]
        self.assertEqual(
            self.dns_core.DNS_SETTING_NAMESERVER | self.dns_core.DNS_SETTING_IPV6,
            settings.Flags,
        )
        self.assertEqual("2620:fe::fe,2620:fe::9", settings.NameServer)

    def test_current_dns_reads_interface_dns_settings_in_order(self) -> None:
        dns_list = self._manager().get_current_dns("Ethernet", "IPv4")

        self.assertEqual(["9.9.9.9", "149.112.112.112"], dns_list)

    def test_current_dns_keeps_only_requested_address_family(self) -> None:
        self.iphlpapi.get_name_server = "9.9.9.9,2620:fe::fe,149.112.112.112,2620:fe::9"

        ipv4_dns = self._manager().get_current_dns("Ethernet", "IPv4")
        ipv6_dns = self._manager().get_current_dns("Ethernet", "IPv6")

        self.assertEqual(["9.9.9.9", "149.112.112.112"], ipv4_dns)
        self.assertEqual(["2620:fe::fe", "2620:fe::9"], ipv6_dns)


if __name__ == "__main__":
    unittest.main()
