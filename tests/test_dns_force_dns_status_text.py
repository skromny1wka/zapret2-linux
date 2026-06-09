from __future__ import annotations

import unittest

from dns.page_plans import build_force_dns_status_plan, build_force_dns_toggle_plan, build_reset_dhcp_result_plan


class ForceDnsStatusTextTests(unittest.TestCase):
    def test_plain_toggle_state_does_not_repeat_status_text(self) -> None:
        enabled_plan = build_force_dns_status_plan(enabled=True)
        disabled_plan = build_force_dns_status_plan(enabled=False)

        self.assertEqual(enabled_plan.text, "")
        self.assertEqual(disabled_plan.text, "")

    def test_action_details_are_shown_without_repeating_toggle_state(self) -> None:
        plan = build_force_dns_status_plan(
            enabled=True,
            details_key="page.network.force_dns.action.enable.description",
            details_fallback="Программа пропишет DNS-серверы для обхода блокировок.",
        )

        self.assertEqual(
            plan.text,
            "Программа пропишет DNS-серверы для обхода блокировок. Это поможет, если провайдер подменяет DNS.",
        )

    def test_toggle_success_uses_human_action_descriptions(self) -> None:
        enable_plan = build_force_dns_toggle_plan(requested_enabled=True, success=True)
        disable_plan = build_force_dns_toggle_plan(requested_enabled=False, success=True)

        self.assertEqual(enable_plan.details_key, "page.network.force_dns.action.enable.description")
        self.assertEqual(disable_plan.details_key, "page.network.force_dns.action.disable.description")

    def test_reset_success_uses_automatic_dns_description(self) -> None:
        plan = build_reset_dhcp_result_plan(success=True, message="", force_dns_active=False)

        self.assertEqual(plan.status_details_key, "page.network.force_dns.action.reset.description")


if __name__ == "__main__":
    unittest.main()
