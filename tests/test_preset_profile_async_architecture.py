from __future__ import annotations

import inspect
import unittest

from profile import commands as profile_commands
from profile.service import ProfilePresetService
from profile.ui.profile_setup_page import ProfileSetupPageBase
from profile.ui.preset_setup_page import PresetSetupPageBase
from presets import display_state
from presets import commands as preset_commands
from presets.ui.common.preset_subpage_base import PresetRawEditorPage
from presets.ui.common.user_presets_page import UserPresetsPageBase
from presets.ui.control.zapret1.page import Zapret1ModeControlPage
from presets.ui.control.zapret2.page import Zapret2ModeControlPage
from presets.user_presets_runtime_service import UserPresetsRuntimeService
from lists.ui.custom_domains_page import CustomDomainsPage
from lists.ui.custom_ipset_page import CustomIpSetPage
from lists.ui.hostlist_page import HostlistPage
from lists.ui.netrogat_page import NetrogatPage
import lists.folder_info_workflow as lists_folder_info_workflow
from lists.editor_workflow import ListsEditorController
from hosts.ui.page import HostsPage
from blobs.ui.page import BlobsPage
from updater.ui.page import ServersPage
from donater.ui.page import PremiumPage
from settings.dpi.page import DpiSettingsPage
from orchestra.ui.blocked_page import OrchestraBlockedPage
from orchestra.ui.locked_page import OrchestraLockedPage
from orchestra.ui.ratings_page import OrchestraRatingsPage
from orchestra.ui.settings_page import OrchestraSettingsPage
from orchestra.ui.whitelist_page import OrchestraWhitelistPage
import dns.page_diagnostics_warning_workflow as dns_diag_workflow
import dns.page_load_workflow as dns_load_workflow
import dns.ui.page as dns_page
from dns.page_workers import DnsPageLoadWorker
import telegram_proxy.ui.diagnostics_workflow as telegram_diag_workflow
import telegram_proxy.ui.proxy_runtime_workflow as telegram_runtime_workflow
import telegram_proxy.ui.page as telegram_page
from telegram_proxy.ui.page import TelegramProxyPage
from telegram_proxy.workers import TelegramProxyDiagnosticsWorker


class PresetProfileAsyncArchitectureTests(unittest.TestCase):
    def test_preset_setup_page_loads_profiles_through_worker(self) -> None:
        refresh_source = inspect.getsource(PresetSetupPageBase.refresh_from_preset_switch)
        activated_source = inspect.getsource(PresetSetupPageBase.on_page_activated)
        init_source = inspect.getsource(PresetSetupPageBase.__init__)
        request_source = inspect.getsource(PresetSetupPageBase._request_profiles_payload)

        self.assertNotIn(".list_profiles(", refresh_source)
        self.assertIn("_request_profiles_payload(force=True)", refresh_source)
        self.assertIn("_request_profiles_payload", activated_source)
        self.assertNotIn("QTimer.singleShot(0, self._request_profiles_payload)", init_source)
        self.assertIn("_profile_payload_dirty", request_source)
        self.assertIn("_profile_payload_loaded_once", request_source)

    def test_refresh_after_switch_uses_profile_snapshot_not_full_list(self) -> None:
        source = inspect.getsource(display_state.resolve_profile_strategy_display_state)

        self.assertNotIn(".list_profiles(", source)
        self.assertIn("get_profile_strategy_display_state", source)

    def test_user_presets_full_metadata_loading_is_worker_only(self) -> None:
        load_source = inspect.getsource(UserPresetsRuntimeService.load_presets)
        watcher_source = inspect.getsource(UserPresetsRuntimeService.reload_presets_from_watcher)

        self.assertNotIn("adapter.load_all_metadata()", load_source)
        self.assertNotIn("adapter.load_all_metadata()", watcher_source)
        self.assertIn("UserPresetsMetadataLoadWorker", load_source)

    def test_profile_commands_reuse_service_cache(self) -> None:
        source = inspect.getsource(profile_commands._profile_preset_service)

        self.assertIn("_preset_service_cache", source)
        self.assertIn("cache[key]", source)

    def test_profile_service_has_selected_preset_snapshot(self) -> None:
        source = inspect.getsource(ProfilePresetService.load_selected_preset)

        self.assertIn("_selected_preset_snapshot", source)
        self.assertIn("_selected_preset_revision", source)

    def test_profile_setup_page_loads_profile_payload_through_worker(self) -> None:
        source = inspect.getsource(ProfileSetupPageBase.reload_current_profile)

        self.assertNotIn("self._controller.load(", source)
        self.assertIn("_request_profile_setup_payload", source)

    def test_preset_selection_state_uses_profile_snapshot(self) -> None:
        source = inspect.getsource(preset_commands._profile_selection_details)

        self.assertNotIn(".list_profiles(", source)
        self.assertNotIn("get_profile_setup(", source)
        self.assertIn("get_profile_selection_details", source)

    def test_control_pages_use_cached_profile_count(self) -> None:
        zapret2_source = inspect.getsource(Zapret2ModeControlPage._load_enabled_profile_count)
        zapret1_source = inspect.getsource(Zapret1ModeControlPage._load_enabled_profile_count)

        self.assertNotIn("count_enabled_profiles", zapret2_source)
        self.assertNotIn("count_enabled_profiles", zapret1_source)
        self.assertIn("get_enabled_profile_count_snapshot", zapret2_source)
        self.assertIn("get_enabled_profile_count_snapshot", zapret1_source)

    def test_raw_preset_editor_loads_file_through_worker(self) -> None:
        source = inspect.getsource(PresetRawEditorPage._load_file)

        self.assertNotIn("self._controller.load_text(", source)
        self.assertIn("_request_raw_preset_text", source)

    def test_lists_pages_load_text_through_worker(self) -> None:
        methods = (
            HostlistPage._load_domains,
            HostlistPage._load_ips,
            HostlistPage._load_exclusions,
            HostlistPage._load_ipru_exclusions,
            CustomDomainsPage._load_domains,
            CustomIpSetPage._load_entries,
            NetrogatPage._load,
        )

        for method in methods:
            source = inspect.getsource(method)
            self.assertNotIn("load_text(", source)
            self.assertIn("request_editor_text", source)

    def test_hostlist_folder_info_uses_qthread_worker(self) -> None:
        workflow_source = inspect.getsource(lists_folder_info_workflow)
        controller_source = inspect.getsource(ListsEditorController)
        request_source = inspect.getsource(HostlistPage._request_folder_info)

        self.assertNotIn("threading.Thread", workflow_source)
        self.assertIn("create_folder_info_load_worker", controller_source)
        self.assertIn("create_folder_info_load_worker", request_source)
        self.assertNotIn("_load_folder_info_worker", request_source)

    def test_hostlist_page_builds_tabs_lazily(self) -> None:
        build_source = inspect.getsource(HostlistPage._build_ui)
        activated_source = inspect.getsource(HostlistPage.on_page_activated)
        switch_source = inspect.getsource(HostlistPage._switch_tab)

        self.assertNotIn("_ensure_panel_built(0)", build_source)
        self.assertIn("_ensure_panel_built(self.stacked.currentIndex())", activated_source)
        self.assertNotIn("panel_domains = self._build_domains_panel()", build_source)
        self.assertNotIn("panel_ips = self._build_ips_panel()", build_source)
        self.assertNotIn("panel_exclusions = self._build_exclusions_panel()", build_source)
        self.assertIn("_ensure_panel_built(index)", switch_source)

    def test_standalone_list_editors_build_ui_on_activation(self) -> None:
        page_classes = (CustomDomainsPage, CustomIpSetPage, NetrogatPage)

        for page_cls in page_classes:
            with self.subTest(page=page_cls.__name__):
                init_source = inspect.getsource(page_cls.__init__)
                activated_source = inspect.getsource(page_cls.on_page_activated)

                self.assertNotIn("self._build_ui()", init_source)
                self.assertIn("_ensure_ui_built()", activated_source)

    def test_profile_setup_builds_hidden_tabs_lazily(self) -> None:
        build_source = inspect.getsource(ProfileSetupPageBase._build_content)
        switch_source = inspect.getsource(ProfileSetupPageBase._switch_strategy_tab)
        apply_source = inspect.getsource(ProfileSetupPageBase._apply_payload)

        self.assertNotIn("self._list_file_text = PlainTextEdit()", build_source)
        self.assertNotIn("self._raw_profile_text = PlainTextEdit()", build_source)
        self.assertIn("_ensure_editor_tab_built()", switch_source)
        self.assertIn("_request_list_file_editor_state()", switch_source)
        self.assertNotIn("_apply_list_file_editor_state", apply_source)

    def test_orchestra_settings_does_not_build_first_tab_in_constructor(self) -> None:
        init_source = inspect.getsource(OrchestraSettingsPage.__init__)
        show_source = inspect.getsource(OrchestraSettingsPage.showEvent)

        self.assertNotIn("self._switch_tab(0)", init_source)
        self.assertIn("self._switch_tab(0)", show_source)

    def test_telegram_proxy_builds_secondary_tabs_lazily(self) -> None:
        setup_source = inspect.getsource(TelegramProxyPage._setup_ui)
        after_source = inspect.getsource(TelegramProxyPage._after_ui_built)
        switch_source = inspect.getsource(TelegramProxyPage._switch_tab)
        timer_source = inspect.getsource(TelegramProxyPage._sync_log_timer)

        self.assertIn("_built_panel_indexes", setup_source)
        self.assertNotIn("build_telegram_proxy_logs_panel(", setup_source)
        self.assertNotIn("build_telegram_proxy_diag_panel(", setup_source)
        self.assertNotIn("_log_timer.start", after_source)
        self.assertIn("_ensure_panel_built(index)", switch_source)
        self.assertIn("self._stacked.currentIndex() == 1", timer_source)

    def test_user_presets_hide_keeps_clean_cache_clean(self) -> None:
        source = inspect.getsource(UserPresetsPageBase.on_page_hidden)

        self.assertNotIn("stop_watching_presets", source)

    def test_hosts_page_first_render_does_not_read_hosts_state_in_constructor(self) -> None:
        init_source = inspect.getsource(HostsPage.__init__)
        build_status_source = inspect.getsource(HostsPage._build_status_section)
        activated_source = inspect.getsource(HostsPage.on_page_activated)

        self.assertNotIn("_run_runtime_init_once()", init_source)
        self.assertNotIn("_get_active_domains()", build_status_source)
        self.assertIn("_run_runtime_init_once()", activated_source)

    def test_lazy_pages_start_runtime_after_activation_not_constructor(self) -> None:
        page_classes = (
            dns_page.NetworkPage,
            HostlistPage,
            CustomDomainsPage,
            CustomIpSetPage,
            NetrogatPage,
            BlobsPage,
            ServersPage,
            TelegramProxyPage,
            PremiumPage,
            DpiSettingsPage,
            OrchestraWhitelistPage,
            OrchestraLockedPage,
            OrchestraBlockedPage,
            OrchestraRatingsPage,
        )

        for page_cls in page_classes:
            with self.subTest(page=page_cls.__name__):
                init_source = inspect.getsource(page_cls.__init__)
                activated_source = inspect.getsource(page_cls.on_page_activated)

                self.assertNotIn("self._run_runtime_init_once()", init_source)
                self.assertIn("self._run_runtime_init_once()", activated_source)

    def test_network_and_telegram_ui_do_not_create_python_threads(self) -> None:
        modules = (
            dns_diag_workflow,
            dns_load_workflow,
            telegram_diag_workflow,
            telegram_runtime_workflow,
            telegram_page,
        )

        for module in modules:
            source = inspect.getsource(module)
            self.assertNotIn("threading.Thread", source)

    def test_dns_page_worker_returns_state_instead_of_calling_page_method(self) -> None:
        workflow_source = inspect.getsource(dns_load_workflow.start_background_loading)
        page_source = inspect.getsource(dns_page.NetworkPage)
        worker_source = inspect.getsource(DnsPageLoadWorker)

        self.assertIn("load_page_data_fn", workflow_source)
        self.assertNotIn("load_data_fn", workflow_source)
        self.assertIn("loaded = pyqtSignal", worker_source)
        self.assertIn("self.loaded.emit", worker_source)
        self.assertNotIn("self._load_data_fn()", worker_source)
        self.assertNotIn("load_data_fn=self._load_data", page_source)

    def test_telegram_diagnostics_worker_uses_progress_signal(self) -> None:
        workflow_source = inspect.getsource(telegram_diag_workflow.start_diagnostics)
        worker_source = inspect.getsource(TelegramProxyDiagnosticsWorker)

        self.assertNotIn("progress_callback=publish_diag_result", workflow_source)
        self.assertIn("worker.progress.connect(publish_diag_result)", workflow_source)
        self.assertIn("progress = pyqtSignal", worker_source)
        self.assertIn("progress_callback=self.progress.emit", worker_source)


if __name__ == "__main__":
    unittest.main()
