"""Автообновление hostlist/ipset из открытых реестров РКН и DPI-списков."""

from __future__ import annotations

import hashlib
import json
import os
import re
import socket
import time
from dataclasses import dataclass, field
from typing import Iterable
from urllib.error import URLError
from urllib.request import Request, urlopen

from lists.core.paths import get_list_base_path, get_list_path, get_lists_base_dir, get_lists_dir
from log.log import log

UPDATE_INTERVAL_SEC = 3600
USER_AGENT = "Zapret-RKN-Sync/1.0"
STATE_FILE_NAME = ".rkn_sync_state.json"
MAX_DNS_RESOLVE_PER_RUN = 400

DOMAIN_SOURCES: tuple[tuple[str, str], ...] = (
    (
        "refilter_domains",
        "https://github.com/1andrevich/Re-filter-lists/releases/latest/download/domains_all.lst",
    ),
    (
        "antifilter_domains",
        "https://antifilter.download/list/domains.lst",
    ),
)

IP_SOURCES: tuple[tuple[str, str], ...] = (
    (
        "refilter_ips",
        "https://github.com/1andrevich/Re-filter-lists/releases/latest/download/ipsum.lst",
    ),
)

JSON_DOMAIN_SOURCES: tuple[tuple[str, str], ...] = (
    ("blockedin_dpi", "https://blockedin.org/api/v3/dpi/"),
    ("rknweb_domains", "https://rknweb.ru/api/v3/domains/"),
)

DOMAIN_LINE_RE = re.compile(r"^[a-z0-9](?:[a-z0-9.-]{0,253}[a-z0-9])?$")


@dataclass(frozen=True, slots=True)
class RknSyncResult:
    changed: bool
    domain_count: int = 0
    ip_count: int = 0
    added_domains: int = 0
    added_ips: int = 0
    resolved_ips: int = 0
    sources_ok: tuple[str, ...] = ()
    sources_failed: tuple[str, ...] = ()
    error: str = ""


@dataclass(slots=True)
class _SyncState:
    last_sync_ts: float = 0.0
    domain_count: int = 0
    ip_count: int = 0
    domain_fingerprint: str = ""
    ip_fingerprint: str = ""


def _state_path() -> str:
    return os.path.join(get_lists_dir(), STATE_FILE_NAME)


def _read_lines(path: str) -> list[str]:
    if not os.path.isfile(path):
        return []
    result: list[str] = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            for raw in handle:
                line = str(raw or "").strip()
                if line and not line.startswith("#"):
                    result.append(line)
    except Exception:
        return []
    return result


def _write_lines_atomic(path: str, lines: Iterable[str], *, header: str = "") -> None:
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)
    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8", newline="\n") as handle:
        if header:
            handle.write(header.rstrip("\n") + "\n")
        for line in lines:
            text = str(line or "").strip()
            if text:
                handle.write(text + "\n")
    os.replace(temp_path, path)


def _normalize_domain(value: str) -> str | None:
    text = str(value or "").strip().lower()
    if not text or text.startswith("#"):
        return None
    if "://" in text:
        text = text.split("://", 1)[1]
    text = text.split("/", 1)[0]
    text = text.split("@", 1)[-1]
    text = text.split(":", 1)[0]
    if text.startswith("*."):
        text = text[2:]
    if text.startswith("."):
        text = text[1:]
    text = text.rstrip(".")
    if not text or "." not in text:
        return None
    if text.replace(".", "").isdigit():
        return None
    if not DOMAIN_LINE_RE.match(text):
        return None
    return text


def _normalize_ip_entry(value: str) -> str | None:
    from lists.ipsets_manager import _normalize_ip_entry

    return _normalize_ip_entry(value)


def _fetch_text(url: str, *, timeout: int = 120) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        payload = response.read()
    return payload.decode("utf-8", errors="replace")


def _parse_domain_lines(text: str) -> set[str]:
    domains: set[str] = set()
    for raw in str(text or "").splitlines():
        domain = _normalize_domain(raw)
        if domain:
            domains.add(domain)
    return domains


def _parse_json_domains(text: str) -> set[str]:
    domains: set[str] = set()
    try:
        payload = json.loads(text)
    except Exception:
        return domains

    items: list = []
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        for key in ("domains", "data", "items", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                items = value
                break

    for item in items:
        if isinstance(item, str):
            domain = _normalize_domain(item)
            if domain:
                domains.add(domain)
            continue
        if isinstance(item, dict):
            for key in ("domain", "name", "host", "hostname", "url"):
                if key in item:
                    domain = _normalize_domain(str(item.get(key) or ""))
                    if domain:
                        domains.add(domain)
                    break
    return domains


def _fetch_domains_from_sources() -> tuple[set[str], list[str], list[str]]:
    merged: set[str] = set()
    ok: list[str] = []
    failed: list[str] = []

    for name, url in DOMAIN_SOURCES + JSON_DOMAIN_SOURCES:
        try:
            text = _fetch_text(url)
            if name.endswith("_domains") and url.endswith("/"):
                batch = _parse_json_domains(text)
            elif url.endswith(".lst") or url.endswith(".txt"):
                batch = _parse_domain_lines(text)
            else:
                batch = _parse_json_domains(text) or _parse_domain_lines(text)
            if not batch:
                failed.append(name)
                continue
            merged.update(batch)
            ok.append(name)
            log(f"RKN sync: {name} -> {len(batch)} доменов", "RKN_SYNC")
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            failed.append(name)
            log(f"RKN sync: источник {name} недоступен: {exc}", "WARNING")

    return merged, ok, failed


def _fetch_ips_from_sources() -> tuple[set[str], list[str], list[str]]:
    merged: set[str] = set()
    ok: list[str] = []
    failed: list[str] = []

    for name, url in IP_SOURCES:
        try:
            text = _fetch_text(url)
            batch: set[str] = set()
            for raw in text.splitlines():
                normalized = _normalize_ip_entry(raw)
                if normalized:
                    batch.add(normalized)
            if not batch:
                failed.append(name)
                continue
            merged.update(batch)
            ok.append(name)
            log(f"RKN sync: {name} -> {len(batch)} IP/CIDR", "RKN_SYNC")
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            failed.append(name)
            log(f"RKN sync: IP-источник {name} недоступен: {exc}", "WARNING")

    return merged, ok, failed


def _resolve_domains_to_ips(domains: Iterable[str], *, limit: int = MAX_DNS_RESOLVE_PER_RUN) -> set[str]:
    resolved: set[str] = set()
    count = 0
    for domain in domains:
        if count >= limit:
            break
        try:
            infos = socket.getaddrinfo(domain, None, type=socket.SOCK_STREAM)
        except Exception:
            continue
        for info in infos:
            ip = info[4][0]
            normalized = _normalize_ip_entry(str(ip))
            if normalized and "/" not in normalized:
                resolved.add(normalized)
        count += 1
    return resolved


def _fingerprint(values: Iterable[str]) -> str:
    payload = "\n".join(sorted(set(values))).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:24]


def get_rkn_sync_interval_sec() -> int:
    return _interval_sec()


def _load_state() -> _SyncState:
    path = _state_path()
    if not os.path.isfile(path):
        return _SyncState()
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
        return _SyncState(
            last_sync_ts=float(raw.get("last_sync_ts") or 0.0),
            domain_count=int(raw.get("domain_count") or 0),
            ip_count=int(raw.get("ip_count") or 0),
            domain_fingerprint=str(raw.get("domain_fingerprint") or ""),
            ip_fingerprint=str(raw.get("ip_fingerprint") or ""),
        )
    except Exception:
        return _SyncState()


def _save_state(*, domain_count: int, ip_count: int, domain_fingerprint: str, ip_fingerprint: str) -> None:
    payload = {
        "last_sync_ts": time.time(),
        "domain_count": int(domain_count),
        "ip_count": int(ip_count),
        "domain_fingerprint": str(domain_fingerprint),
        "ip_fingerprint": str(ip_fingerprint),
    }
    path = _state_path()
    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    os.replace(temp_path, path)


def _is_enabled() -> bool:
    try:
        from settings.store import get_rkn_lists_auto_update_enabled

        return bool(get_rkn_lists_auto_update_enabled())
    except Exception:
        return True


def _interval_sec() -> int:
    try:
        from settings.store import get_rkn_lists_auto_update_interval_sec

        return max(300, int(get_rkn_lists_auto_update_interval_sec()))
    except Exception:
        return UPDATE_INTERVAL_SEC


def should_run_rkn_sync(*, force: bool = False) -> bool:
    if force:
        return True
    if not _is_enabled():
        return False
    state = _load_state()
    if state.last_sync_ts <= 0:
        return True
    return (time.time() - state.last_sync_ts) >= _interval_sec()


def sync_rkn_registry_lists(*, force: bool = False) -> RknSyncResult:
    """Скачивает реестры РКН/DPI, обновляет russia-blacklist и ipset-all."""
    if not should_run_rkn_sync(force=force):
        state = _load_state()
        return RknSyncResult(
            changed=False,
            domain_count=state.domain_count,
            ip_count=state.ip_count,
        )

    if not _is_enabled() and not force:
        return RknSyncResult(changed=False, error="auto update disabled")

    os.makedirs(get_lists_dir(), exist_ok=True)
    os.makedirs(get_lists_base_dir(), exist_ok=True)

    blacklist_path = get_list_path("russia-blacklist")
    ipset_base_path = get_list_base_path("ipset-all")

    existing_domains = {_normalize_domain(x) for x in _read_lines(blacklist_path)}
    existing_domains.discard(None)
    existing_ips = {_normalize_ip_entry(x) for x in _read_lines(ipset_base_path)}
    existing_ips.discard(None)

    remote_domains, domain_sources_ok, domain_sources_failed = _fetch_domains_from_sources()
    if not remote_domains:
        return RknSyncResult(
            changed=False,
            error="не удалось загрузить домены ни из одного источника",
            sources_failed=tuple(domain_sources_failed),
        )

    remote_ips, ip_sources_ok, ip_sources_failed = _fetch_ips_from_sources()
    merged_domains = set(existing_domains)
    merged_domains.update(remote_domains)

    previous_remote_domains = set(existing_domains)
    new_domains = sorted(remote_domains - previous_remote_domains)
    resolved_ips = _resolve_domains_to_ips(new_domains) if new_domains else set()

    merged_ips = set(existing_ips)
    merged_ips.update(remote_ips)
    merged_ips.update(resolved_ips)

    sorted_domains = sorted(merged_domains)
    sorted_ips = sorted(merged_ips, key=lambda item: (":" in item, item))

    domain_fp = _fingerprint(sorted_domains)
    ip_fp = _fingerprint(sorted_ips)
    state = _load_state()
    changed = domain_fp != state.domain_fingerprint or ip_fp != state.ip_fingerprint

    if changed:
        header = (
            "# Автообновление из реестров РКН/DPI (Zapret RKN sync)\n"
            f"# Обновлено: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"# Источники: {', '.join(domain_sources_ok) or 'local'}\n"
        )
        _write_lines_atomic(blacklist_path, sorted_domains, header=header)
        ip_header = (
            "# Автообновление IP из реестра РКН (Zapret RKN sync)\n"
            f"# Обновлено: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"# Источники: {', '.join(ip_sources_ok) or 'local'}\n"
        )
        _write_lines_atomic(ipset_base_path, sorted_ips, header=ip_header)

        try:
            from lists.hostlists_manager import rebuild_other_files
            from lists.ipsets_manager import rebuild_ipset_all_files

            rebuild_ipset_all_files()
            rebuild_other_files()
        except Exception as exc:
            log(f"RKN sync: ошибка пересборки lists: {exc}", "WARNING")

        _save_state(
            domain_count=len(sorted_domains),
            ip_count=len(sorted_ips),
            domain_fingerprint=domain_fp,
            ip_fingerprint=ip_fp,
        )
        log(
            "RKN sync: обновлено "
            f"domains={len(sorted_domains)} (+{len(merged_domains) - len(existing_domains)}), "
            f"ips={len(sorted_ips)} (+{len(merged_ips) - len(existing_ips)}), "
            f"resolved={len(resolved_ips)}",
            "SUCCESS",
        )
    else:
        _save_state(
            domain_count=len(sorted_domains),
            ip_count=len(sorted_ips),
            domain_fingerprint=domain_fp,
            ip_fingerprint=ip_fp,
        )
        log("RKN sync: изменений нет", "RKN_SYNC")

    return RknSyncResult(
        changed=changed,
        domain_count=len(sorted_domains),
        ip_count=len(sorted_ips),
        added_domains=max(0, len(merged_domains) - len(existing_domains)),
        added_ips=max(0, len(merged_ips) - len(existing_ips)),
        resolved_ips=len(resolved_ips),
        sources_ok=tuple(domain_sources_ok + ip_sources_ok),
        sources_failed=tuple(domain_sources_failed + ip_sources_failed),
    )


def restart_dpi_after_rkn_sync(*, runtime_feature) -> bool:
    if runtime_feature is None:
        return False
    try:
        from winws_runtime.runtime.commands import is_dpi_running, restart_dpi_async

        if not is_dpi_running(runtime_feature=runtime_feature):
            return False
        restart_dpi_async(runtime_feature=runtime_feature)
        log("RKN sync: перезапуск DPI для применения новых списков", "INFO")
        return True
    except Exception as exc:
        log(f"RKN sync: не удалось перезапустить DPI: {exc}", "WARNING")
        return False


def run_rkn_sync_with_optional_restart(
    *,
    runtime_feature=None,
    force: bool = False,
    restart_on_change: bool = True,
) -> RknSyncResult:
    result = sync_rkn_registry_lists(force=force)
    if result.changed and restart_on_change:
        restart_dpi_after_rkn_sync(runtime_feature=runtime_feature)
    return result
