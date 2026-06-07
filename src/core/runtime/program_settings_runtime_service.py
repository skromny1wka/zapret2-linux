from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
import weakref


@dataclass(frozen=True, slots=True)
class ProgramSettingsSnapshot:
    revision: tuple[bool, bool, bool, bool, bool]
    auto_dpi_enabled: bool
    gui_autostart_enabled: bool
    hide_to_tray_on_minimize_close: bool
    defender_disabled: bool
    max_blocked: bool


_warmed_hide_to_tray_lock = RLock()
_warmed_hide_to_tray_on_minimize_close: bool | None = None
_warmed_program_settings_fast_snapshot: tuple[bool, bool, bool, bool, bool] | None = None


def store_warmed_hide_to_tray_on_minimize_close(enabled: bool | None) -> None:
    global _warmed_hide_to_tray_on_minimize_close
    normalized = None if enabled is None else bool(enabled)
    with _warmed_hide_to_tray_lock:
        _warmed_hide_to_tray_on_minimize_close = normalized


def peek_warmed_hide_to_tray_on_minimize_close() -> bool | None:
    with _warmed_hide_to_tray_lock:
        return _warmed_hide_to_tray_on_minimize_close


def store_warmed_program_settings_fast_snapshot(
    *,
    auto_dpi_enabled: bool | None,
    gui_autostart_enabled: bool | None,
    hide_to_tray_on_minimize_close: bool | None,
    defender_disabled: bool | None = None,
    max_blocked: bool | None = None,
) -> None:
    """Stores settings.json values already read during startup."""

    global _warmed_program_settings_fast_snapshot
    with _warmed_hide_to_tray_lock:
        if (
            auto_dpi_enabled is None
            or gui_autostart_enabled is None
            or hide_to_tray_on_minimize_close is None
            or defender_disabled is None
            or max_blocked is None
        ):
            _warmed_program_settings_fast_snapshot = None
            return
        _warmed_program_settings_fast_snapshot = (
            bool(auto_dpi_enabled),
            bool(gui_autostart_enabled),
            bool(hide_to_tray_on_minimize_close),
            bool(defender_disabled),
            bool(max_blocked),
        )


def peek_warmed_program_settings_fast_snapshot() -> tuple[bool, bool, bool, bool, bool] | None:
    with _warmed_hide_to_tray_lock:
        return _warmed_program_settings_fast_snapshot


class ProgramSettingsRuntimeService:
    """Service-owned snapshot for shared program settings toggle state.

    Эти настройки используются сразу несколькими control-страницами. Страницы
    не должны каждая по отдельности считать себя владельцем синхронизации
    состояния через on_page_activated().
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._hide_to_tray_on_minimize_close_cache: bool | None = (
            peek_warmed_hide_to_tray_on_minimize_close()
        )
        warmed_snapshot = self._snapshot_from_warmed_fast_values()
        self._snapshot: ProgramSettingsSnapshot | None = warmed_snapshot
        self._subscribers: list[object] = []

    @staticmethod
    def _build_snapshot(
        *,
        auto_dpi_enabled: bool,
        gui_autostart_enabled: bool,
        hide_to_tray_on_minimize_close: bool,
        defender_disabled: bool,
        max_blocked: bool,
    ) -> ProgramSettingsSnapshot:
        revision = (
            bool(auto_dpi_enabled),
            bool(gui_autostart_enabled),
            bool(hide_to_tray_on_minimize_close),
            bool(defender_disabled),
            bool(max_blocked),
        )
        return ProgramSettingsSnapshot(
            revision=revision,
            auto_dpi_enabled=bool(auto_dpi_enabled),
            gui_autostart_enabled=bool(gui_autostart_enabled),
            hide_to_tray_on_minimize_close=bool(hide_to_tray_on_minimize_close),
            defender_disabled=bool(defender_disabled),
            max_blocked=bool(max_blocked),
        )

    def _snapshot_from_warmed_fast_values(self) -> ProgramSettingsSnapshot | None:
        warmed = peek_warmed_program_settings_fast_snapshot()
        if warmed is None:
            return None
        (
            auto_dpi_enabled,
            gui_autostart_enabled,
            hide_to_tray_on_minimize_close,
            defender_disabled,
            max_blocked,
        ) = warmed
        warmed_hide_to_tray = peek_warmed_hide_to_tray_on_minimize_close()
        if warmed_hide_to_tray is not None:
            hide_to_tray_on_minimize_close = bool(warmed_hide_to_tray)
        self._hide_to_tray_on_minimize_close_cache = bool(hide_to_tray_on_minimize_close)
        return self._build_snapshot(
            auto_dpi_enabled=auto_dpi_enabled,
            gui_autostart_enabled=gui_autostart_enabled,
            hide_to_tray_on_minimize_close=hide_to_tray_on_minimize_close,
            defender_disabled=defender_disabled,
            max_blocked=max_blocked,
        )

    @staticmethod
    def _read_auto_dpi_enabled() -> bool:
        try:
            from settings.store import get_dpi_autostart

            return bool(get_dpi_autostart())
        except Exception:
            return False

    @staticmethod
    def _read_gui_autostart_enabled() -> bool:
        try:
            from settings.store import get_gui_autostart_enabled

            return bool(get_gui_autostart_enabled())
        except Exception:
            return False

    @staticmethod
    def _read_defender_disabled() -> bool:
        try:
            from windows_features.defender_manager import WindowsDefenderManager

            return bool(WindowsDefenderManager().is_defender_disabled())
        except Exception:
            return False

    @staticmethod
    def _read_hide_to_tray_on_minimize_close() -> bool:
        try:
            from settings.store import get_hide_to_tray_on_minimize_close

            return bool(get_hide_to_tray_on_minimize_close())
        except Exception:
            return False

    @staticmethod
    def _read_max_blocked() -> bool:
        try:
            from windows_features.max_blocker import is_max_blocked

            return bool(is_max_blocked())
        except Exception:
            return False

    @staticmethod
    def _read_remembered_defender_disabled() -> bool:
        try:
            from settings.store import get_defender_disabled_memory

            return bool(get_defender_disabled_memory())
        except Exception:
            return False

    @staticmethod
    def _read_remembered_max_blocked() -> bool:
        try:
            from settings.store import get_max_blocked

            return bool(get_max_blocked())
        except Exception:
            return False

    def _read_fast_snapshot(self) -> ProgramSettingsSnapshot:
        auto_dpi_enabled = self._read_auto_dpi_enabled()
        gui_autostart_enabled = self._read_gui_autostart_enabled()
        hide_to_tray_on_minimize_close = self._read_hide_to_tray_on_minimize_close()
        return self._build_snapshot(
            auto_dpi_enabled=auto_dpi_enabled,
            gui_autostart_enabled=gui_autostart_enabled,
            hide_to_tray_on_minimize_close=hide_to_tray_on_minimize_close,
            defender_disabled=self._read_remembered_defender_disabled(),
            max_blocked=self._read_remembered_max_blocked(),
        )

    def _read_system_status_snapshot(self) -> ProgramSettingsSnapshot:
        with self._lock:
            snapshot = self._snapshot
        if snapshot is None:
            snapshot = self._read_fast_snapshot()
        defender_disabled = self._read_defender_disabled()
        max_blocked = self._read_max_blocked()
        return self._build_snapshot(
            auto_dpi_enabled=bool(snapshot.auto_dpi_enabled),
            gui_autostart_enabled=bool(snapshot.gui_autostart_enabled),
            hide_to_tray_on_minimize_close=bool(snapshot.hide_to_tray_on_minimize_close),
            defender_disabled=defender_disabled,
            max_blocked=max_blocked,
        )

    def read_snapshot(self) -> ProgramSettingsSnapshot:
        with self._lock:
            snapshot = self._snapshot
        if snapshot is not None:
            return snapshot
        return self.refresh_fast()

    def publish_snapshot(self, snapshot: ProgramSettingsSnapshot) -> bool:
        should_notify = False
        with self._lock:
            previous = self._snapshot
            self._hide_to_tray_on_minimize_close_cache = bool(
                snapshot.hide_to_tray_on_minimize_close
            )
            if previous is None or previous.revision != snapshot.revision:
                self._snapshot = snapshot
                should_notify = True
            else:
                snapshot = previous

        if should_notify:
            self._notify(snapshot)
        return should_notify

    def peek_hide_to_tray_on_minimize_close(self, *, default: bool = False) -> bool:
        with self._lock:
            snapshot = self._snapshot
            cached = self._hide_to_tray_on_minimize_close_cache
        if snapshot is not None:
            return bool(snapshot.hide_to_tray_on_minimize_close)
        if cached is not None:
            return bool(cached)
        return bool(default)

    def remember_hide_to_tray_on_minimize_close(self, enabled: bool) -> bool:
        enabled = bool(enabled)
        with self._lock:
            self._hide_to_tray_on_minimize_close_cache = enabled
            snapshot = self._snapshot
        if snapshot is None:
            return False
        updated = ProgramSettingsSnapshot(
            revision=(
                bool(snapshot.auto_dpi_enabled),
                bool(snapshot.gui_autostart_enabled),
                enabled,
                bool(snapshot.defender_disabled),
                bool(snapshot.max_blocked),
            ),
            auto_dpi_enabled=bool(snapshot.auto_dpi_enabled),
            gui_autostart_enabled=bool(snapshot.gui_autostart_enabled),
            hide_to_tray_on_minimize_close=enabled,
            defender_disabled=bool(snapshot.defender_disabled),
            max_blocked=bool(snapshot.max_blocked),
        )
        return self.publish_snapshot(updated)

    @staticmethod
    def _make_callback_ref(callback):
        try:
            return weakref.WeakMethod(callback)
        except TypeError:
            try:
                return weakref.ref(callback)
            except TypeError:
                return lambda: callback

    def _resolve_callback(self, ref):
        try:
            return ref()
        except Exception:
            return None

    def _notify(self, snapshot: ProgramSettingsSnapshot) -> None:
        callbacks: list = []
        with self._lock:
            alive_refs: list[object] = []
            for ref in self._subscribers:
                callback = self._resolve_callback(ref)
                if callback is None:
                    continue
                alive_refs.append(ref)
                callbacks.append(callback)
            self._subscribers = alive_refs

        for callback in callbacks:
            try:
                callback(snapshot)
            except Exception:
                pass

    def load_snapshot(self, *, refresh: bool = False) -> ProgramSettingsSnapshot:
        with self._lock:
            snapshot = self._snapshot
        if snapshot is None or refresh:
            return self.refresh_fast()
        return snapshot

    def refresh(self) -> ProgramSettingsSnapshot:
        return self.refresh_fast()

    def refresh_fast(self) -> ProgramSettingsSnapshot:
        snapshot = self._read_fast_snapshot()
        self.publish_snapshot(snapshot)
        return snapshot

    def refresh_system_status(self) -> ProgramSettingsSnapshot:
        snapshot = self._read_system_status_snapshot()
        self.publish_snapshot(snapshot)
        return snapshot

    def subscribe(self, callback, *, emit_initial: bool = False):
        ref = self._make_callback_ref(callback)
        with self._lock:
            self._subscribers.append(ref)

        if emit_initial:
            try:
                callback(self.load_snapshot())
            except Exception:
                pass

        def _unsubscribe() -> None:
            with self._lock:
                self._subscribers = [item for item in self._subscribers if item is not ref]

        return _unsubscribe
