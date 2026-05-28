from __future__ import annotations


_RESTART_PRIORITY = {
    "": 0,
    "schedule": 1,
    "now": 2,
}


def normalize_restart_request(value: str | None) -> str:
    restart = str(value or "").strip().lower()
    if restart not in _RESTART_PRIORITY:
        return ""
    return restart


def merge_restart_request(current: str | None, requested: str | None) -> str:
    current_restart = normalize_restart_request(current)
    requested_restart = normalize_restart_request(requested)
    if _RESTART_PRIORITY[requested_restart] > _RESTART_PRIORITY[current_restart]:
        return requested_restart
    return current_restart


__all__ = ["merge_restart_request", "normalize_restart_request"]
