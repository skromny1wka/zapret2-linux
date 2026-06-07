from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AboutTabSwitchPlan:
    current_index: int
    route_key: str
    init_support: bool
    init_help: bool
    init_kvn: bool


@dataclass(slots=True)
class AboutSubscriptionPlan:
    icon_name: str
    icon_color: str
    label_text: str

TAB_KEYS = ("about", "support", "help", "kvn")

def build_tab_switch_plan(
    *,
    index: int,
    support_initialized: bool,
    help_initialized: bool,
    kvn_initialized: bool,
) -> AboutTabSwitchPlan:
    safe_index = max(0, min(int(index), len(TAB_KEYS) - 1))
    route_key = TAB_KEYS[safe_index]
    return AboutTabSwitchPlan(
        current_index=safe_index,
        route_key=route_key,
        init_support=(safe_index == 1 and not support_initialized),
        init_help=(safe_index == 2 and not help_initialized),
        init_kvn=(safe_index == 3 and not kvn_initialized),
    )

def resolve_tab_index(key: str) -> int | None:
    normalized = str(key or "").strip().lower()
    if normalized in TAB_KEYS:
        return TAB_KEYS.index(normalized)
    return None

def build_subscription_status_plan(
    *,
    is_premium: bool,
    days: int | None,
    free_text: str,
    premium_active_text: str,
    premium_days_template: str,
    free_icon_color: str,
    premium_icon_color: str,
) -> AboutSubscriptionPlan:
    if is_premium:
        if days is not None:
            label_text = premium_days_template.format(days=days)
        else:
            label_text = premium_active_text
        return AboutSubscriptionPlan(
            icon_name="fa5s.star",
            icon_color=premium_icon_color,
            label_text=label_text,
        )

    return AboutSubscriptionPlan(
        icon_name="fa5s.user",
        icon_color=free_icon_color,
        label_text=free_text,
    )
