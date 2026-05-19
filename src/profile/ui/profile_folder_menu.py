from __future__ import annotations

from collections.abc import Callable

from profile.folders import (
    create_profile_folder,
    delete_profile_folder,
    load_profile_folder_state,
    move_profile_folder_by_step,
    rename_profile_folder,
    reset_profile_folders,
    set_profile_folder_collapsed,
)
from ui.widgets.folder_context_menu import FolderMenuActions, FolderMenuLabels, show_folder_context_menu


def show_profile_folder_menu(
    *,
    parent,
    folder_key: str,
    global_pos,
    refresh_fn: Callable[[], object],
    log_fn: Callable[[str, str], object] | None = None,
) -> None:
    show_folder_context_menu(
        parent=parent,
        folder_key=folder_key,
        global_pos=global_pos,
        actions=FolderMenuActions(
            load_state=load_profile_folder_state,
            create_folder=create_profile_folder,
            rename_folder=rename_profile_folder,
            delete_folder=delete_profile_folder,
            move_folder_by_step=move_profile_folder_by_step,
            set_folder_collapsed=set_profile_folder_collapsed,
            reset_folders=reset_profile_folders,
        ),
        labels=FolderMenuLabels(
            reset_title="Сбросить папки profile-ов",
            reset_body="Вернём стандартные папки profile-ов и разложим их заново по начальному правилу.",
            create_subtitle="Новая папка появится сразу после «Общие».",
            rename_subtitle="Изменится только название папки в интерфейсе. Profile останутся на месте.",
            delete_body="Profile из этой папки не удалятся. Они перейдут в «Общие».",
            action_error_suffix="profile-ов",
        ),
        refresh_fn=refresh_fn,
        log_fn=log_fn,
    )


__all__ = ["show_profile_folder_menu"]
