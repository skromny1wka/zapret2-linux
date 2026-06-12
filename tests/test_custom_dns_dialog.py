from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QWidget


class CustomDnsDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = QApplication.instance() or QApplication([])

    def test_dialog_adds_edits_and_deletes_custom_dns_entries(self) -> None:
        from dns.ui.custom_dns_dialog import CustomDnsDialog

        parent = QWidget()
        parent.resize(640, 480)
        dialog = CustomDnsDialog(parent, servers=[])

        dialog.nameEdit.setText("Мой DNS")
        dialog.primaryEdit.setText("8.8.8.8")
        dialog.secondaryEdit.setText("1.1.1.1")

        self.assertTrue(dialog.save_current())
        self.assertEqual(len(dialog.servers()), 1)
        self.assertEqual(dialog.servers()[0]["name"], "Мой DNS")
        self.assertEqual(dialog.servers()[0]["ipv4"], ["8.8.8.8", "1.1.1.1"])

        dialog.nameEdit.setText("Рабочий DNS")
        dialog.primaryEdit.setText("9.9.9.9")
        dialog.secondaryEdit.setText("")

        self.assertTrue(dialog.save_current())
        self.assertEqual(dialog.servers()[0]["name"], "Рабочий DNS")
        self.assertEqual(dialog.servers()[0]["ipv4"], ["9.9.9.9"])

        self.assertTrue(dialog.delete_current())
        self.assertEqual(dialog.servers(), [])

    def test_dialog_requires_name_and_primary_dns(self) -> None:
        from dns.ui.custom_dns_dialog import CustomDnsDialog

        parent = QWidget()
        parent.resize(640, 480)
        dialog = CustomDnsDialog(parent, servers=[])

        self.assertFalse(dialog.save_current())
        self.assertIn("название", dialog.warningLabel.text().lower())

        dialog.nameEdit.setText("Мой DNS")

        self.assertFalse(dialog.save_current())
        self.assertIn("основной DNS", dialog.warningLabel.text())

    def test_dialog_rejects_invalid_ipv4_addresses(self) -> None:
        from dns.ui.custom_dns_dialog import CustomDnsDialog

        parent = QWidget()
        parent.resize(640, 480)
        dialog = CustomDnsDialog(parent, servers=[])

        dialog.nameEdit.setText("Мой DNS")
        dialog.primaryEdit.setText("bad")

        self.assertFalse(dialog.save_current())
        self.assertIn("IPv4", dialog.warningLabel.text())

        dialog.primaryEdit.setText("8.8.8.8")
        dialog.secondaryEdit.setText("bad")

        self.assertFalse(dialog.save_current())
        self.assertIn("IPv4", dialog.warningLabel.text())


if __name__ == "__main__":
    unittest.main()
