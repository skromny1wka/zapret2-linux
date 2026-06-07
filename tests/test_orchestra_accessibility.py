import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from orchestra.ui.blocked_page import BlockedDomainRow, OrchestraBlockedPage
from orchestra.ui.locked_page import LockedDomainRow, OrchestraLockedPage
from orchestra.ui.ratings_page import OrchestraRatingsPage
from orchestra.ui.whitelist_page import OrchestraWhitelistPage, WhitelistDomainRow


class _OrchestraFeatureStub:
    ASKEY_ALL = ("tcp", "udp")


class OrchestraAccessibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_locked_page_main_controls_are_named_for_screen_reader(self) -> None:
        page = OrchestraLockedPage(orchestra_feature=_OrchestraFeatureStub())
        self.addCleanup(page.deleteLater)

        self.assertEqual(page.domain_input.accessibleName(), "Домен для залочки стратегии")
        self.assertIn("example.com", page.domain_input.accessibleDescription())
        self.assertEqual(page.proto_combo.accessibleName(), "Протокол залочки стратегии, выбрано: TCP")
        self.assertIn("TCP или UDP", page.proto_combo.accessibleDescription())
        self.assertEqual(page.strat_spin.accessibleName(), "Номер стратегии для залочки, выбрано: 1")
        self.assertEqual(page.lock_btn.accessibleName(), "Залочить стратегию для домена")
        self.assertEqual(page.search_input.accessibleName(), "Поиск по залоченным доменам")
        self.assertEqual(page.refresh_btn.accessibleName(), "Обновить список залоченных стратегий")
        self.assertEqual(page.unlock_all_btn.accessibleName(), "Разлочить все стратегии")

        page.proto_combo.setCurrentIndex(1)
        page.strat_spin.setValue(7)

        self.assertEqual(page.proto_combo.accessibleName(), "Протокол залочки стратегии, выбрано: UDP")
        self.assertEqual(page.strat_spin.accessibleName(), "Номер стратегии для залочки, выбрано: 7")

    def test_blocked_page_main_controls_are_named_for_screen_reader(self) -> None:
        page = OrchestraBlockedPage(orchestra_feature=_OrchestraFeatureStub())
        self.addCleanup(page.deleteLater)

        self.assertEqual(page.domain_input.accessibleName(), "Домен для блокировки стратегии")
        self.assertIn("example.com", page.domain_input.accessibleDescription())
        self.assertEqual(page.proto_combo.accessibleName(), "Протокол блокировки стратегии, выбрано: TCP")
        self.assertEqual(page.strat_spin.accessibleName(), "Номер блокируемой стратегии, выбрано: 1")
        self.assertEqual(page.block_btn.accessibleName(), "Заблокировать стратегию для домена")
        self.assertEqual(page.search_input.accessibleName(), "Поиск по заблокированным доменам")
        self.assertEqual(page.refresh_btn.accessibleName(), "Обновить чёрный список стратегий")
        self.assertEqual(page.unblock_all_btn.accessibleName(), "Очистить пользовательские блокировки")

        page.proto_combo.setCurrentIndex(1)
        page.strat_spin.setValue(9)

        self.assertEqual(page.proto_combo.accessibleName(), "Протокол блокировки стратегии, выбрано: UDP")
        self.assertEqual(page.strat_spin.accessibleName(), "Номер блокируемой стратегии, выбрано: 9")

    def test_whitelist_page_main_controls_are_named_for_screen_reader(self) -> None:
        page = OrchestraWhitelistPage(orchestra_feature=_OrchestraFeatureStub())
        self.addCleanup(page.deleteLater)

        self.assertEqual(page.restart_warning.accessibleName(), "Предупреждение: изменения белого списка применятся после перезапуска оркестратора")
        self.assertEqual(page.domain_input.accessibleName(), "Домен для белого списка")
        self.assertEqual(page.add_btn.accessibleName(), "Добавить домен в белый список")
        self.assertEqual(page.search_input.accessibleName(), "Поиск по белому списку")
        self.assertEqual(page.clear_user_btn.accessibleName(), "Очистить пользовательские домены белого списка")

    def test_ratings_page_main_controls_are_named_for_screen_reader(self) -> None:
        page = OrchestraRatingsPage(orchestra_feature=_OrchestraFeatureStub())
        self.addCleanup(page.deleteLater)

        self.assertEqual(page.filter_input.accessibleName(), "Фильтр рейтингов по домену")
        self.assertEqual(page.refresh_btn.accessibleName(), "Обновить рейтинги стратегий")
        self.assertEqual(page.stats_label.accessibleName(), "Статистика рейтингов: Загрузка...")
        self.assertEqual(page.history_text.accessibleName(), "История рейтингов стратегий")
        self.assertIn("результаты обучения", page.history_text.accessibleDescription())

    def test_row_controls_include_domain_protocol_and_strategy(self) -> None:
        locked_row = LockedDomainRow("example.com", 3, "tcp")
        blocked_row = BlockedDomainRow("blocked.example", 5, "udp", is_default=False)
        whitelist_row = WhitelistDomainRow("safe.example", is_default=False)
        self.addCleanup(locked_row.deleteLater)
        self.addCleanup(blocked_row.deleteLater)
        self.addCleanup(whitelist_row.deleteLater)

        self.assertEqual(locked_row.accessibleName(), "Залоченная стратегия: example.com, TCP, стратегия 3")
        self.assertEqual(locked_row.strat_spin.accessibleName(), "Стратегия для example.com TCP, выбрано: 3")
        self.assertEqual(locked_row._delete_btn.accessibleName(), "Разлочить example.com TCP")
        locked_row.strat_spin.setValue(8)
        self.assertEqual(locked_row.strat_spin.accessibleName(), "Стратегия для example.com TCP, выбрано: 8")

        self.assertEqual(blocked_row.accessibleName(), "Заблокированная стратегия: blocked.example, UDP, стратегия 5")
        self.assertEqual(blocked_row.strat_spin.accessibleName(), "Заблокированная стратегия для blocked.example UDP, выбрано: 5")
        self.assertEqual(blocked_row._add_btn.accessibleName(), "Добавить ещё одну блокировку для blocked.example UDP")
        self.assertEqual(blocked_row._delete_btn.accessibleName(), "Разблокировать blocked.example UDP, стратегия 5")

        self.assertEqual(whitelist_row.accessibleName(), "Домен белого списка: safe.example")
        self.assertEqual(whitelist_row._delete_btn.accessibleName(), "Удалить safe.example из белого списка")


if __name__ == "__main__":
    unittest.main()
