from __future__ import annotations

from dataclasses import dataclass

from settings.mode import ENGINE_WINWS2


@dataclass(frozen=True, slots=True)
class PreparedLaunchPresetText:
    text: str
    warnings: tuple[str, ...] = ()

    @property
    def changed(self) -> bool:
        return False


def is_winws2_circular_preset_text(source_content: str) -> bool:
    lowered = str(source_content or "").lower()
    return (
        "(circular)" in lowered
        or "--lua-desync=circular" in lowered
        or "--lua-desync=circular_quality" in lowered
    )


def prepare_winws2_preset_text_for_launch(
    source_content: str,
    *,
    source_name: str = "",
    source_is_circular: bool = False,
) -> PreparedLaunchPresetText:
    from profile.parser import parse_preset_text
    from profile.winws2_transport import parse_out_range_expression, validate_winws2_payload_filter

    raw_text = str(source_content or "")
    source = parse_preset_text(
        raw_text,
        engine=ENGINE_WINWS2,
        source_name=source_name,
    )
    _ = source_is_circular

    for profile in source.profiles or ():
        if not bool(getattr(profile, "enabled", True)):
            continue

        for segment in profile.segments:
            if segment.kind != "strategy_filter":
                continue
            profile_name = str(getattr(profile, "display_name", "") or f"profile {profile.index + 1}").strip()
            name = str(segment.name or "").strip().lower()
            value = str(segment.value or "").strip()
            if name in {"--in-range", "--out-range"} and parse_out_range_expression(value, raw_line=segment.text) is None:
                raise ValueError(f"{profile_name}: неверное значение {name}={value}")
            if name == "--payload" and not validate_winws2_payload_filter(value):
                raise ValueError(f"{profile_name}: неверное значение --payload={value}")

    return PreparedLaunchPresetText(
        text=raw_text,
    )


__all__ = [
    "PreparedLaunchPresetText",
    "is_winws2_circular_preset_text",
    "prepare_winws2_preset_text_for_launch",
]
