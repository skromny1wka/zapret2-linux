from __future__ import annotations

from collections.abc import Callable

from folders.defaults import PINNED_FOLDER_KEY
from presets.folders import (
    create_preset_folder,
    delete_preset_folder,
    load_preset_folder_state,
    move_preset_folder_by_step,
    rename_preset_folder,
    reset_preset_folders,
    set_preset_folder_collapsed,
)
from ui.widgets.folder_context_menu import FolderMenuActions, FolderMenuLabels, FolderNameDialog, show_folder_context_menu


def show_preset_folder_menu(
    *,
    parent,
    scope_key: str,
    folder_key: str,
    global_pos,
    refresh_fn: Callable[[], object],
    log_fn: Callable[[str, str], object] | None = None,
) -> None:
    scope = str(scope_key or "")
    show_folder_context_menu(
        parent=parent,
        folder_key=folder_key,
        global_pos=global_pos,
        actions=FolderMenuActions(
            load_state=lambda: load_preset_folder_state(scope),
            create_folder=lambda name: create_preset_folder(scope, name),
            rename_folder=lambda key, name: rename_preset_folder(scope, key, name),
            delete_folder=lambda key: delete_preset_folder(scope, key),
            move_folder_by_step=lambda key, direction: move_preset_folder_by_step(scope, key, direction),
            set_folder_collapsed=lambda key, collapsed: set_preset_folder_collapsed(scope, key, collapsed),
            reset_folders=lambda: reset_preset_folders(scope),
        ),
        labels=FolderMenuLabels(
            reset_title="Сбросить папки preset-ов",
            reset_body="Вернём стандартные папки и разложим preset-ы заново по начальному правилу.",
            create_subtitle="Новая папка появится сразу после «Общие».",
            rename_subtitle="Изменится только название папки в интерфейсе. Preset-ы останутся на месте.",
            delete_body="Preset-ы из этой папки не удалятся. Они перейдут в «Общие».",
            action_error_suffix="preset-ов",
        ),
        refresh_fn=refresh_fn,
        log_fn=log_fn,
        service_folder_keys={PINNED_FOLDER_KEY},
    )


PresetFolderNameDialog = FolderNameDialog

__all__ = ["PresetFolderNameDialog", "show_preset_folder_menu"]
