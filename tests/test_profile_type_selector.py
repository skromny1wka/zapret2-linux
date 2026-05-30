from __future__ import annotations

import unittest
from types import SimpleNamespace


class _Button:
    def __init__(self, checked: bool = False) -> None:
        self._checked = bool(checked)
        self.calls: list[bool] = []

    def isChecked(self) -> bool:  # noqa: N802
        return self._checked

    def setChecked(self, checked: bool) -> None:  # noqa: N802
        value = bool(checked)
        self.calls.append(value)
        self._checked = value


class ProfileTypeSelectorTests(unittest.TestCase):
    def test_set_button_checked_skips_duplicate_state(self) -> None:
        from profile.ui.widgets.profile_type_selector import set_button_checked_if_changed

        button = _Button(True)

        self.assertFalse(set_button_checked_if_changed(button, True))
        self.assertEqual(button.calls, [])

        self.assertTrue(set_button_checked_if_changed(button, False))
        self.assertEqual(button.calls, [False])

    def test_set_active_profile_types_skips_duplicate_button_states(self) -> None:
        from profile.ui.widgets.profile_type_selector import ProfileTypeSelector

        all_button = _Button(False)
        tcp_button = _Button(True)
        udp_button = _Button(False)
        selector = SimpleNamespace(
            _buttons={
                "all": all_button,
                "tcp": tcp_button,
                "udp": udp_button,
            },
            blockSignals=lambda _blocked: None,
            _has_other_selected=lambda: any(
                button.isChecked()
                for key, button in selector._buttons.items()
                if key != "all"
            ),
        )

        ProfileTypeSelector.set_active_profile_types(selector, {"tcp"})

        self.assertEqual(all_button.calls, [])
        self.assertEqual(tcp_button.calls, [])
        self.assertEqual(udp_button.calls, [])

    def test_profile_types_signal_skips_duplicate_state(self) -> None:
        from profile.ui.widgets.profile_type_selector import ProfileTypeSelector

        emitted: list[set[str]] = []
        selector = SimpleNamespace(
            get_active_profile_types=lambda: {"all"},
            profile_types_changed=SimpleNamespace(emit=emitted.append),
        )

        changed = ProfileTypeSelector._emit_profile_types_changed_if_needed(selector, {"all"})

        self.assertFalse(changed)
        self.assertEqual(emitted, [])


if __name__ == "__main__":
    unittest.main()
