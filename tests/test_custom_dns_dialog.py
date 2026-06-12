from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QWidget


class CustomDnsDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = QApplication.instance() or QApplication([])

    def test_dialog_creates_one_custom_dns_entry(self) -> None:
        from dns.ui.custom_dns_dialog import CustomDnsDialog

        parent = QWidget()
        parent.resize(640, 480)
        dialog = CustomDnsDialog(parent)

        self.assertEqual(dialog.titleLabel.text(), "Добавить свой DNS")
        self.assertEqual(dialog.yesButton.text(), "Добавить")
        self.assertFalse(hasattr(dialog, "serversList"))

        dialog.nameEdit.setText("Мой DNS")
        dialog.primaryEdit.setText("8.8.8.8")
        dialog.secondaryEdit.setText("1.1.1.1")

        self.assertTrue(dialog.validate())
        self.assertEqual(dialog.server()["name"], "Мой DNS")
        self.assertEqual(dialog.server()["ipv4"], ["8.8.8.8", "1.1.1.1"])
        self.assertEqual(dialog.servers(), [dialog.server()])

    def test_dialog_edits_one_existing_custom_dns_entry(self) -> None:
        from dns.ui.custom_dns_dialog import CustomDnsDialog

        parent = QWidget()
        parent.resize(640, 480)
        dialog = CustomDnsDialog(
            parent,
            server={"id": "cloudflare", "name": "Cloudflare", "ipv4": ["1.1.1.1"], "ipv6": []},
        )

        self.assertEqual(dialog.titleLabel.text(), "Редактировать свой DNS")
        self.assertEqual(dialog.yesButton.text(), "Сохранить")
        self.assertEqual(dialog.nameEdit.text(), "Cloudflare")
        self.assertEqual(dialog.primaryEdit.text(), "1.1.1.1")

        dialog.nameEdit.setText("Рабочий DNS")
        dialog.primaryEdit.setText("9.9.9.9")

        self.assertTrue(dialog.validate())
        self.assertEqual(dialog.server()["id"], "cloudflare")
        self.assertEqual(dialog.server()["name"], "Рабочий DNS")
        self.assertEqual(dialog.server()["ipv4"], ["9.9.9.9"])

    def test_dialog_requires_name_and_primary_dns(self) -> None:
        from dns.ui.custom_dns_dialog import CustomDnsDialog

        parent = QWidget()
        parent.resize(640, 480)
        dialog = CustomDnsDialog(parent)

        self.assertFalse(dialog.validate())
        self.assertIn("название", dialog.warningLabel.text().lower())

        dialog.nameEdit.setText("Мой DNS")

        self.assertFalse(dialog.validate())
        self.assertIn("основной DNS", dialog.warningLabel.text())

    def test_dialog_rejects_invalid_ipv4_addresses(self) -> None:
        from dns.ui.custom_dns_dialog import CustomDnsDialog

        parent = QWidget()
        parent.resize(640, 480)
        dialog = CustomDnsDialog(parent)

        dialog.nameEdit.setText("Мой DNS")
        dialog.primaryEdit.setText("bad")

        self.assertFalse(dialog.validate())
        self.assertIn("IPv4", dialog.warningLabel.text())

        dialog.primaryEdit.setText("8.8.8.8")
        dialog.secondaryEdit.setText("bad")

        self.assertFalse(dialog.validate())
        self.assertIn("IPv4", dialog.warningLabel.text())


if __name__ == "__main__":
    unittest.main()
