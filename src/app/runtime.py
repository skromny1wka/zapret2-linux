from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from app.feature_assembly import build_app_features
from app.features import AppFeatures
from app.state_access import AppStateAccess, build_app_state_access


@dataclass(frozen=True, slots=True)
class AppRuntime:
    paths: Any
    state: AppStateAccess
    features: AppFeatures


def build_app_runtime(*, initial_ui_state=None, feature_deps_factory: Callable[[AppStateAccess], Any]) -> AppRuntime:
    from pathlib import Path

    from config.config import MAIN_DIRECTORY
    from core.paths import AppPaths

    paths = AppPaths(
        user_root=Path(MAIN_DIRECTORY).resolve(),
        local_root=Path(MAIN_DIRECTORY).resolve(),
    )
    state = build_app_state_access(initial_ui_state)
    feature_deps = feature_deps_factory(state)
    return AppRuntime(
        paths=paths,
        state=state,
        features=build_app_features(deps=feature_deps, paths=paths, state=state),
    )
