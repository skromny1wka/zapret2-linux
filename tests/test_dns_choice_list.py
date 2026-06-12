from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget


class DnsChoiceListTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = QApplication.instance() or QApplication([])

    def test_choice_list_uses_delegate_rows_for_static_dns_choices(self) -> None:
        from dns.ui.choice_list import DnsChoiceListWidget
        from dns.ui.cards import DNSProviderCard

        view = DnsChoiceListWidget()
        auto = view.add_auto_choice("Автоматически (DHCP)")
        provider = view.add_provider(
            "Google DNS",
            {
                "desc": "Надёжный",
                "ipv4": ["8.8.8.8"],
                "ipv6": ["2001:4860:4860::8888"],
                "icon": "fa5b.google",
                "doh": "https://dns.google/dns-query",
            },
            show_ipv6=True,
        )

        self.assertEqual(len(view.findChildren(DNSProviderCard)), 0)
        self.assertEqual(auto.property("selected"), False)

        provider.set_selected(True)

        self.assertTrue(provider.property("selected"))
        self.assertEqual(provider.accessibleName(), "DNS Google DNS, выбран")
        self.assertGreater(view.sizeHintForRow(0), 0)

    def test_choice_list_emits_same_selection_signals_as_old_cards(self) -> None:
        from dns.ui.choice_list import DnsChoiceListWidget

        view = DnsChoiceListWidget()
        auto_item = view.add_auto_choice("Автоматически (DHCP)").item
        provider_item = view.add_provider(
            "Cloudflare",
            {"desc": "Быстрый", "ipv4": ["1.1.1.1"], "ipv6": []},
            show_ipv6=False,
        ).item
        custom_item = view.set_custom_choice(QWidget())
        selected: list[str] = []
        view.auto_selected.connect(lambda: selected.append("auto"))
        view.provider_selected.connect(lambda name, _data: selected.append(name))
        view.custom_selected.connect(lambda: selected.append("custom"))

        view.activate_item(auto_item)
        view.activate_item(provider_item)
        view.activate_item(custom_item)

        self.assertEqual(selected, ["auto", "Cloudflare", "custom"])
        self.assertEqual(auto_item.flags() & Qt.ItemFlag.ItemIsEnabled, Qt.ItemFlag.ItemIsEnabled)


if __name__ == "__main__":
    unittest.main()
