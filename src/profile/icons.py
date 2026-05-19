from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath, PureWindowsPath
import hashlib
import re

from profile.match_filters import filter_values


@dataclass(frozen=True)
class ProfileIconSpec:
    icon_name: str
    color: str


_KNOWN_ICONS: dict[str, ProfileIconSpec] = {
    "youtube": ProfileIconSpec("simple:youtube:YT", "#FF0000"),
    "googlevideo": ProfileIconSpec("simple:youtube:YT", "#FF0000"),
    "discord": ProfileIconSpec("simple:discord:DI", "#5865F2"),
    "discord-updates": ProfileIconSpec("simple:discord:DI", "#5865F2"),
    "telegram": ProfileIconSpec("simple:telegram:TG", "#229ED9"),
    "whatsapp": ProfileIconSpec("simple:whatsapp:WA", "#25D366"),
    "facebook": ProfileIconSpec("simple:facebook:FB", "#1877F2"),
    "instagram": ProfileIconSpec("simple:instagram:IN", "#E4405F"),
    "twitter": ProfileIconSpec("simple:x:X", "#000000"),
    "twimg": ProfileIconSpec("simple:x:X", "#000000"),
    "steam": ProfileIconSpec("simple:steam:ST", "#66C0F4"),
    "github": ProfileIconSpec("simple:github:GH", "#F0F3F6"),
    "twitch": ProfileIconSpec("simple:twitch:TW", "#9146FF"),
    "soundcloud": ProfileIconSpec("simple:soundcloud:SC", "#FF5500"),
    "itch": ProfileIconSpec("simple:itchdotio:IT", "#FA5C5C"),
    "google": ProfileIconSpec("simple:google:GO", "#4285F4"),
    "amazon": ProfileIconSpec("simple:amazon:AM", "#FF9900"),
}

_NAMED_COLORS: dict[str, str] = {
    "cloudflare": "#F38020",
    "ovh": "#123F6D",
    "warp": "#F6821F",
    "timeweb": "#2F80ED",
    "zapretkvn": "#31C48D",
    "roblox": "#E2231A",
    "lol": "#C89B3C",
    "lol-ru": "#C89B3C",
    "lol-euw": "#C89B3C",
    "rutracker": "#6AA2FF",
    "rutor": "#6AA2FF",
}

_FALLBACK_PALETTE: tuple[str, ...] = (
    "#14B8A6",
    "#3B82F6",
    "#8B5CF6",
    "#EC4899",
    "#F97316",
    "#22C55E",
    "#06B6D4",
    "#EAB308",
)

_FALLBACK_SIMPLE_ICON_SLUGS: tuple[str, ...] = (
    "simpleicons",
    "abstract",
    "codementor",
    "codecrafters",
    "codeforces",
    "codesandbox",
    "codepen",
    "polymerproject",
)


def resolve_profile_icon(display_name: object, match_lines: tuple[str, ...] | list[str] = ()) -> ProfileIconSpec:
    identity = _profile_identity(display_name, tuple(match_lines or ()))
    if identity in _KNOWN_ICONS:
        return _KNOWN_ICONS[identity]

    color = _NAMED_COLORS.get(identity) or _color_from_seed(identity)
    initials = _initials_from_identity(identity)
    return ProfileIconSpec(f"simple:{_simple_fallback_slug(identity)}:{initials}", color)


def _profile_identity(display_name: object, match_lines: tuple[str, ...]) -> str:
    candidates: list[str] = []
    candidates.extend(_resource_values(match_lines))
    candidates.append(str(display_name or ""))
    for candidate in candidates:
        normalized = _normalize_identity(candidate)
        if normalized:
            return normalized
    return "profile"


def _resource_values(match_lines: tuple[str, ...]) -> list[str]:
    return [
        *filter_values(match_lines, "--hostlist"),
        *filter_values(match_lines, "--ipset"),
        *filter_values(match_lines, "--hostlist-domains"),
        *filter_values(match_lines, "--ipset-ip"),
    ]


def _normalize_identity(value: str) -> str:
    text = str(value or "").strip().replace("\\", "/").lower()
    if not text:
        return ""
    if "/" in text:
        text = PurePosixPath(text).name
    else:
        text = PureWindowsPath(text).name
    text = re.sub(r"\.(txt|lst|list|json)$", "", text, flags=re.IGNORECASE)
    for prefix in ("ipset-", "hostlist-", "list-"):
        if text.startswith(prefix):
            text = text[len(prefix):]
    text = re.split(r"[\s(]", text, maxsplit=1)[0]
    text = text.strip(".-_")
    if "." in text:
        parts = [part for part in text.split(".") if part]
        if len(parts) >= 2:
            text = parts[-2]
    return re.sub(r"[^a-z0-9а-яё-]+", "-", text, flags=re.IGNORECASE).strip("-") or "profile"


def _initials_from_identity(identity: str) -> str:
    words = [part for part in re.split(r"[^a-z0-9а-яё]+", str(identity or ""), flags=re.IGNORECASE) if part]
    if not words:
        return "P"
    if len(words) == 1:
        word = words[0]
        return (word[:2] if len(word) > 1 else word[:1]).upper()
    return (words[0][:1] + words[1][:1]).upper()


def _color_from_seed(seed: str) -> str:
    digest = hashlib.sha1(str(seed or "profile").encode("utf-8")).digest()
    return _FALLBACK_PALETTE[digest[0] % len(_FALLBACK_PALETTE)]


def _simple_fallback_slug(seed: str) -> str:
    digest = hashlib.sha1(str(seed or "profile").encode("utf-8")).digest()
    return _FALLBACK_SIMPLE_ICON_SLUGS[digest[1] % len(_FALLBACK_SIMPLE_ICON_SLUGS)]


__all__ = ["ProfileIconSpec", "resolve_profile_icon"]
