from __future__ import annotations

import inspect
import unittest

from app.feature_facades.dns import build_dns_feature
from dns import page_workers
import dns.public as dns_public


class DnsWorkerArchitectureTests(unittest.TestCase):
    def test_network_action_workers_use_public_commands_not_feature_object(self) -> None:
        feature_source = inspect.getsource(build_dns_feature)
        worker_source = "\n".join(
            (
                inspect.getsource(page_workers.DnsForceDnsActionWorker),
                inspect.getsource(page_workers.DnsFlushCacheWorker),
                inspect.getsource(page_workers.DnsIspWarningWorker),
                inspect.getsource(page_workers.DnsApplyWorker),
            )
        )

        self.assertNotIn("dns_feature=feature", feature_source)
        self.assertNotIn("self._dns =", worker_source)
        self.assertNotIn("self._dns.", worker_source)
        self.assertIn("dns_public.get_force_dns_status", worker_source)
        self.assertIn("dns_public.enable_force_dns", worker_source)
        self.assertIn("dns_public.disable_force_dns", worker_source)
        self.assertIn("dns_public.flush_dns_cache", worker_source)
        self.assertIn("dns_public.apply_auto_dns", worker_source)
        self.assertIn("dns_public.apply_provider_dns", worker_source)
        self.assertIn("dns_public.apply_custom_dns", worker_source)
        self.assertIn("dns_public.refresh_dns_info", worker_source)
        self.assertIn("dns_public.is_isp_dns_warning_shown", worker_source)
        self.assertIn("dns_public.mark_isp_dns_warning_shown", worker_source)
        self.assertIn("dns_public.normalize_adapter_alias", worker_source)
        self.assertIn("enable_force_dns", inspect.getsource(dns_public.enable_force_dns))
        self.assertIn("apply_custom_dns", inspect.getsource(dns_public.apply_custom_dns))


if __name__ == "__main__":
    unittest.main()
