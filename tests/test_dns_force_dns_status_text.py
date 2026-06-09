from __future__ import annotations

import unittest

from dns.page_plans import build_force_dns_status_plan


class ForceDnsStatusTextTests(unittest.TestCase):
    def test_plain_toggle_state_does_not_repeat_status_text(self) -> None:
        enabled_plan = build_force_dns_status_plan(enabled=True)
        disabled_plan = build_force_dns_status_plan(enabled=False)

        self.assertEqual(enabled_plan.text, "")
        self.assertEqual(disabled_plan.text, "")

    def test_action_details_are_shown_without_repeating_toggle_state(self) -> None:
        plan = build_force_dns_status_plan(
            enabled=True,
            details_key="page.network.force_dns.status.details.adapters_applied",
            details_kwargs={"ok_count": 2, "total": 3},
            details_fallback="2/3 адаптеров",
        )

        self.assertEqual(plan.text, "2/3 адаптеров")


if __name__ == "__main__":
    unittest.main()
