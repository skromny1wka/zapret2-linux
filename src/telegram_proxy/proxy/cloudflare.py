from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode


@dataclass(frozen=True, slots=True)
class CloudflareFallbackConfig:
    enabled: bool = False
    domains: tuple[str, ...] = ()
    worker_enabled: bool = False
    worker_domains: tuple[str, ...] = ()


def _is_valid_domain(value: str) -> bool:
    if not value or len(value) > 253:
        return False
    if value.startswith(".") or value.endswith("."):
        return False
    labels = value.split(".")
    if len(labels) < 2:
        return False
    for label in labels:
        if not label or len(label) > 63:
            return False
        if label[0] == "-" or label[-1] == "-":
            return False
        if not all(ch.isalnum() or ch == "-" for ch in label):
            return False
    return len(labels[-1]) >= 2 and any(ch.isalpha() for ch in labels[-1])


def normalize_domain_list(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        raw_items = value.replace(",", " ").replace(";", " ").split()
    elif isinstance(value, (list, tuple, set)):
        raw_items: list[str] = []
        for entry in value:
            if isinstance(entry, str):
                raw_items.extend(entry.replace(",", " ").replace(";", " ").split())
    else:
        raw_items = []

    result: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        domain = item.strip().lower()
        if domain in seen or not _is_valid_domain(domain):
            continue
        seen.add(domain)
        result.append(domain)
    return tuple(result)


def should_try_cloudflare(config: CloudflareFallbackConfig | None) -> bool:
    if config is None:
        return False
    if config.enabled and config.domains:
        return True
    return bool(config.worker_enabled and config.worker_domains)


def build_cloudflare_domains(dc: int, config: CloudflareFallbackConfig) -> list[str]:
    result: list[str] = []
    for base_domain in config.domains:
        result.append(f"kws{int(dc)}.{base_domain}")
        result.append(f"kws{int(dc)}-1.{base_domain}")
    return result


def build_worker_path(dst: str, dc: int) -> str:
    return "/apiws?" + urlencode({"dst": str(dst or ""), "dc": str(int(dc or 0))})


__all__ = [
    "CloudflareFallbackConfig",
    "build_cloudflare_domains",
    "build_worker_path",
    "normalize_domain_list",
    "should_try_cloudflare",
]
