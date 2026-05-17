"""Workflow синхронизации Hosts state с реальным файлом hosts."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class HostsActiveDomainsReadPlan:
    active_domains: set[str]
    error_kind: Literal["read_error", "no_access"] | None
    error_message: str
    hosts_path: str
    should_hide_error: bool


def build_active_domains_read_plan(
    *,
    runtime_state,
    hosts_path: str,
    read_active_domains_fn: Callable[[], set[str]],
) -> HostsActiveDomainsReadPlan:
    """Готовит результат чтения активных доменов без прямой работы с UI."""
    if runtime_state.error_message:
        return HostsActiveDomainsReadPlan(
            active_domains=set(),
            error_kind="read_error",
            error_message=str(runtime_state.error_message),
            hosts_path=hosts_path,
            should_hide_error=False,
        )

    if not runtime_state.accessible:
        return HostsActiveDomainsReadPlan(
            active_domains=set(),
            error_kind="no_access",
            error_message="",
            hosts_path=hosts_path,
            should_hide_error=False,
        )

    return HostsActiveDomainsReadPlan(
        active_domains=set(read_active_domains_fn()),
        error_kind=None,
        error_message="",
        hosts_path=hosts_path,
        should_hide_error=True,
    )
