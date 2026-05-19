from __future__ import annotations

import re
from pathlib import Path

from core.paths import AppPaths
from settings.mode import ENGINE_WINWS1, ENGINE_WINWS2
from settings.store import get_user_profiles_settings, set_user_profiles_settings

from .models import EngineName, Profile
from .parser import parse_preset_text
from .strategy_catalog import load_strategy_catalogs


_PORTS_RE = re.compile(r"^[0-9*,~-]+$")
_SLUG_RE = re.compile(r"[^a-z0-9а-яё]+", flags=re.IGNORECASE)
_RU_TRANSLIT = str.maketrans({
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh",
    "з": "z", "и": "i", "й": "i", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
    "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "c",
    "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu",
    "я": "ya",
})


def create_user_profile(paths: AppPaths, *, name: str, protocol: str, ports: str) -> str:
    clean_name = _clean_name(name)
    clean_protocol = _clean_protocol(protocol)
    clean_ports = _clean_ports(ports)
    profile_id = _unique_profile_id(_slugify(clean_name))
    hostlist = f"lists/{profile_id}.txt"
    ipset = f"lists/ipset-{profile_id}.txt"

    lists_root = Path(paths.user_root) / "lists"
    lists_root.mkdir(parents=True, exist_ok=True)
    _ensure_file(lists_root / f"{profile_id}.txt")
    _ensure_file(lists_root / f"ipset-{profile_id}.txt")

    settings = get_user_profiles_settings()
    profiles = dict(settings.get("profiles") or {})
    profiles[profile_id] = {
        "name": clean_name,
        "protocol": clean_protocol,
        "ports": clean_ports,
        "hostlist": hostlist,
        "ipset": ipset,
    }
    set_user_profiles_settings({"version": 1, "profiles": profiles})
    return profile_id


def load_user_profile_templates(paths: AppPaths, engine: EngineName | str) -> dict[str, Profile]:
    normalized_engine = str(engine or "").strip().lower()
    profiles = get_user_profiles_settings().get("profiles") or {}
    result: dict[str, Profile] = {}
    for profile_id, row in sorted(profiles.items()):
        text = _profile_text(row, paths=paths, engine=normalized_engine)
        if not text:
            continue
        try:
            preset = parse_preset_text(text, engine=normalized_engine, source_name="user_profiles")
        except Exception:
            continue
        if preset.profiles:
            result[f"user:{profile_id}"] = preset.profiles[0]
    return result


def _profile_text(row: object, *, paths: AppPaths, engine: str) -> str:
    if not isinstance(row, dict):
        return ""
    name = _clean_name(row.get("name"))
    protocol = _clean_protocol(row.get("protocol"))
    ports = _clean_ports(row.get("ports"))
    hostlist = str(row.get("hostlist") or "").strip()
    if not hostlist:
        return ""
    lines = [
        f"--name={name}",
        f"--filter-{protocol}={ports}",
        f"--hostlist={hostlist}",
    ]
    if engine == ENGINE_WINWS2:
        lines.append("--lua-desync=pass")
    elif engine == ENGINE_WINWS1:
        lines.extend(_first_strategy_lines(paths, engine=engine, protocol=protocol))
    return "\n".join(lines) + "\n"


def _first_strategy_lines(paths: AppPaths, *, engine: str, protocol: str) -> list[str]:
    catalog = load_strategy_catalogs(paths, engine).get(protocol) or {}
    for entry in catalog.values():
        lines = [line.strip() for line in str(entry.args or "").splitlines() if line.strip()]
        if lines:
            return lines
    return []


def _clean_name(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError("Название profile не должно быть пустым")
    return text


def _clean_protocol(value: object) -> str:
    protocol = str(value or "").strip().lower()
    if protocol not in {"tcp", "udp"}:
        raise ValueError("Тип profile должен быть TCP или UDP")
    return protocol


def _clean_ports(value: object) -> str:
    text = str(value or "").strip().replace(" ", "")
    if not text:
        raise ValueError("Порты profile не должны быть пустыми")
    if not _PORTS_RE.match(text):
        raise ValueError("Порты можно указать числами, диапазонами и запятыми")
    return text


def _slugify(value: str) -> str:
    text = value.strip().lower().translate(_RU_TRANSLIT)
    text = _SLUG_RE.sub("-", text).strip("-")
    return text or "profile"


def _unique_profile_id(base: str) -> str:
    profiles = get_user_profiles_settings().get("profiles") or {}
    candidate = base
    counter = 2
    while candidate in profiles:
        candidate = f"{base}-{counter}"
        counter += 1
    return candidate


def _ensure_file(path: Path) -> None:
    if path.exists():
        return
    path.write_text("", encoding="utf-8")
