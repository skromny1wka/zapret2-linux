from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from main.window_lifecycle_cleanup import (
    cleanup_theme_for_close,
    cleanup_threaded_pages_for_close,
    cleanup_visual_and_proxy_resources_for_close,
    persist_window_geometry,
)


@dataclass(frozen=True, slots=True)
class ApplicationLifecycleWindowPort:
    _window: Any

    def persist_geometry(self, *, context: str, level: str = "DEBUG") -> None:
        persist_window_geometry(self._window, context=context, level=level)

    def cleanup_theme(self) -> None:
        cleanup_theme_for_close(self._window)

    def cleanup_threaded_pages(self) -> None:
        cleanup_threaded_pages_for_close(self._window)

    def cleanup_visual_and_proxy_resources(self, *, telegram_proxy_feature) -> None:
        cleanup_visual_and_proxy_resources_for_close(
            self._window,
            telegram_proxy_feature=telegram_proxy_feature,
        )


def build_application_lifecycle_window_port(window) -> ApplicationLifecycleWindowPort:
    return ApplicationLifecycleWindowPort(window)


__all__ = ["ApplicationLifecycleWindowPort", "build_application_lifecycle_window_port"]
