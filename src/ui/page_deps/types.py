from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DnsPageDeps:
    dns_feature: object


@dataclass(frozen=True, slots=True)
class HostsPageDeps:
    hosts_feature: object


@dataclass(frozen=True, slots=True)
class PremiumPageDeps:
    premium_feature: object
    subscription_state_store: object


__all__ = [
    "DnsPageDeps",
    "HostsPageDeps",
    "PremiumPageDeps",
]
