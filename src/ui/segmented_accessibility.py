from __future__ import annotations

from ui.accessibility import set_control_accessibility, set_state_text


def _clean_text(text: object) -> str:
    return " ".join(str(text or "").strip().split())


def _segmented_current_key(widget) -> str:
    key = _clean_text(getattr(widget, "_currentRouteKey", ""))
    if key:
        return key
    try:
        return str(widget.currentItem() or "").strip()
    except Exception:
        return ""


def set_segmented_items_accessibility(
    widget,
    *,
    name: str,
    labels: dict[str, object] | None = None,
    selected_word: str = "выбрано",
    unselected_word: str = "не выбрано",
) -> None:
    if widget is None:
        return
    title = _clean_text(name)
    if not title:
        return
    current_key = _segmented_current_key(widget)
    try:
        items = dict(getattr(widget, "items", {}) or {})
    except Exception:
        items = {}
    accessible_labels = {str(key): value for key, value in dict(labels or {}).items()}
    for key, item in items.items():
        try:
            label = _clean_text(accessible_labels.get(str(key), item.text()))
        except Exception:
            label = ""
        if not label:
            continue
        state = selected_word if str(key) == current_key else unselected_word
        text = f"{title}: {label}, {state}"
        set_control_accessibility(item, name=text)
        set_state_text(item, text)


__all__ = ["set_segmented_items_accessibility"]
