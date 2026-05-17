"""Workflow применения DNS на странице Network."""

from __future__ import annotations


def apply_auto_dns_quick(
    *,
    dns_feature,
    adapters: list,
    build_result_plan_fn,
    refresh_adapters_dns_fn,
    log_fn,
) -> None:
    if not adapters:
        return

    result = dns_feature.apply_auto_dns(adapters)
    plan = build_result_plan_fn(
        adapter_count=len(adapters),
        success_count=result.affected_count,
    )
    _apply_result_plan(plan, refresh_adapters_dns_fn=refresh_adapters_dns_fn, log_fn=log_fn)


def apply_provider_dns_quick(
    *,
    dns_feature,
    adapters: list,
    name: str,
    data: dict,
    ipv6_available: bool,
    build_provider_plan_fn,
    build_result_plan_fn,
    refresh_adapters_dns_fn,
    log_fn,
) -> None:
    if not adapters:
        return

    provider_plan = build_provider_plan_fn(
        name=name,
        data=data,
        ipv6_available=ipv6_available,
    )
    if not provider_plan.valid:
        if provider_plan.log_message:
            log_fn(provider_plan.log_message, provider_plan.log_level or "WARNING")
        return

    result = dns_feature.apply_provider_dns(
        adapters,
        provider_plan.ipv4,
        provider_plan.ipv6,
        ipv6_available=ipv6_available,
    )
    result_plan = build_result_plan_fn(
        name=name,
        adapter_count=len(adapters),
        success_count=result.affected_count,
        ipv6_available=ipv6_available,
        ipv6=provider_plan.ipv6,
    )
    _apply_result_plan(result_plan, refresh_adapters_dns_fn=refresh_adapters_dns_fn, log_fn=log_fn)


def apply_custom_dns_quick(
    *,
    dns_feature,
    adapters: list,
    primary: str,
    secondary: str | None,
    build_result_plan_fn,
    refresh_adapters_dns_fn,
    log_fn,
) -> None:
    if not adapters or not primary:
        return

    result = dns_feature.apply_custom_dns(adapters, primary, secondary)
    plan = build_result_plan_fn(
        primary=primary,
        adapter_count=len(adapters),
        success_count=result.affected_count,
    )
    _apply_result_plan(plan, refresh_adapters_dns_fn=refresh_adapters_dns_fn, log_fn=log_fn)


def _apply_result_plan(plan, *, refresh_adapters_dns_fn, log_fn) -> None:
    if plan.log_message:
        log_fn(plan.log_message, plan.log_level or "INFO")
    if plan.should_refresh:
        refresh_adapters_dns_fn()
