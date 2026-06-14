from __future__ import annotations

import ast
import ctypes
import importlib
import sys
import types
import unittest
from pathlib import Path


DNS_CORE = Path(__file__).resolve().parents[1] / "src" / "dns" / "dns_core.py"


def _source() -> str:
    return DNS_CORE.read_text(encoding="utf-8")


def _module() -> ast.Module:
    return ast.parse(_source())


class _FakeWindowsApi:
    def __getattr__(self, _name: str):
        return self


def _load_dns_core():
    try:
        import winreg  # noqa: F401
    except ModuleNotFoundError:
        sys.modules.setdefault("winreg", types.SimpleNamespace())

    if not hasattr(ctypes, "windll"):
        ctypes.windll = _FakeWindowsApi()

    sys.modules.pop("dns.dns_core", None)
    return importlib.import_module("dns.dns_core")


class _FakeIpHelper:
    def __init__(self, dns_core):
        self.dns_core = dns_core
        self.call = None

    def SetInterfaceDnsSettings(self, _guid, settings_ptr):  # noqa: N802
        settings = ctypes.cast(
            settings_ptr,
            ctypes.POINTER(self.dns_core.DNS_INTERFACE_SETTINGS3),
        ).contents
        first_property = settings.ServerProperties[0]
        self.call = {
            "version": settings.Version,
            "flags": settings.Flags,
            "name_server": settings.NameServer,
            "property_count": settings.cServerProperties,
            "property_version": first_property.Version,
            "property_index": first_property.ServerIndex,
            "property_type": first_property.Type,
            "template": first_property.Property.DohSettings.contents.Template,
            "doh_flags": first_property.Property.DohSettings.contents.Flags,
        }
        return 0


class DnsCoreWinApiTests(unittest.TestCase):
    def test_dns_writes_use_set_interface_dns_settings(self) -> None:
        source = _source()

        self.assertIn("SetInterfaceDnsSettings", source)
        self.assertIn("DNS_INTERFACE_SETTINGS", source)
        self.assertIn("DNS_INTERFACE_SETTINGS3", source)
        self.assertIn("DNS_SETTING_NAMESERVER", source)
        self.assertIn("DNS_SETTING_DOH", source)

    def test_doh_is_not_written_through_registry_keys(self) -> None:
        source = _source()

        self.assertNotIn("DohFlags", source)
        self.assertNotIn("DohTemplate", source)
        self.assertNotIn("DohAutoUpgrade", source)
        self.assertNotIn("InterfaceSpecificParameters", source)

    def test_winapi_constants_match_windows_sdk(self) -> None:
        module = _module()
        constants = {
            node.targets[0].id: ast.literal_eval(node.value)
            for node in module.body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id.startswith(("DNS_", "DnsServer"))
        }

        self.assertEqual(constants["DNS_INTERFACE_SETTINGS_VERSION1"], 0x0001)
        self.assertEqual(constants["DNS_INTERFACE_SETTINGS_VERSION3"], 0x0003)
        self.assertEqual(constants["DNS_SETTING_IPV6"], 0x0001)
        self.assertEqual(constants["DNS_SETTING_NAMESERVER"], 0x0002)
        self.assertEqual(constants["DNS_SETTING_DOH"], 0x1000)
        self.assertEqual(constants["DNS_SERVER_PROPERTY_VERSION1"], 0x0001)
        self.assertEqual(constants["DnsServerDohProperty"], 1)
        self.assertEqual(constants["DNS_DOH_SERVER_SETTINGS_ENABLE"], 0x0002)
        self.assertEqual(constants["DNS_DOH_SERVER_SETTINGS_FALLBACK_TO_UDP"], 0x0004)

    def test_winapi_doh_write_passes_server_property_to_iphlpapi(self) -> None:
        dns_core = _load_dns_core()
        fake_iphlpapi = _FakeIpHelper(dns_core)
        dns_core.iphlpapi = fake_iphlpapi
        dns_core._guid_from_string = lambda _guid: dns_core.GUID()
        dns_core.is_doh_supported = lambda: True

        ok = dns_core.set_dns_via_winapi(
            "{C78087CA-DCB3-4993-B9D1-7CC33D0A288B}",
            ["9.9.9.9", "185.222.222.222"],
            is_ipv6=False,
            doh_templates={"9.9.9.9": "https://dns.quad9.net/dns-query"},
        )

        self.assertTrue(ok)
        self.assertEqual(fake_iphlpapi.call["version"], 3)
        self.assertEqual(
            fake_iphlpapi.call["flags"],
            dns_core.DNS_SETTING_NAMESERVER | dns_core.DNS_SETTING_DOH,
        )
        self.assertEqual(fake_iphlpapi.call["name_server"], "9.9.9.9,185.222.222.222")
        self.assertEqual(fake_iphlpapi.call["property_count"], 1)
        self.assertEqual(fake_iphlpapi.call["property_version"], 1)
        self.assertEqual(fake_iphlpapi.call["property_index"], 0)
        self.assertEqual(fake_iphlpapi.call["property_type"], dns_core.DnsServerDohProperty)
        self.assertEqual(fake_iphlpapi.call["template"], "https://dns.quad9.net/dns-query")
        self.assertEqual(
            fake_iphlpapi.call["doh_flags"],
            dns_core.DNS_DOH_SERVER_SETTINGS_ENABLE
            | dns_core.DNS_DOH_SERVER_SETTINGS_FALLBACK_TO_UDP,
        )

    def test_doh_support_requires_windows_build_with_dns_interface_settings3(self) -> None:
        dns_core = _load_dns_core()

        dns_core.get_windows_version = lambda: (10, 0, 19045)
        self.assertFalse(dns_core.is_doh_supported())

        dns_core.get_windows_version = lambda: (10, 0, 19645)
        self.assertTrue(dns_core.is_doh_supported())

        dns_core.get_windows_version = lambda: (10, 0, 22000)
        self.assertTrue(dns_core.is_doh_supported())


if __name__ == "__main__":
    unittest.main()
