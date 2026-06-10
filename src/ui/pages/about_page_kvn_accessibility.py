"""Accessibility helpers for About Zapret KVN cards."""

from __future__ import annotations

from ui.accessibility import set_control_accessibility


def set_kvn_card_accessibility(card, *, action_name: str, description: str) -> None:
    """Задаёт понятный текст кликабельной карточке Zapret KVN."""

    set_control_accessibility(card, name=action_name, description=description)
    button = getattr(card, "button", None)
    if button is not None:
        set_control_accessibility(button, name=action_name, description=description)


__all__ = ["set_kvn_card_accessibility"]
