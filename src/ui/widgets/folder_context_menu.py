from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from qfluentwidgets import BodyLabel, CaptionLabel, LineEdit, MessageBox, MessageBoxBase, RoundMenu, SubtitleLabel

from ui.fluent_widgets import style_semantic_caption_label
from ui.presets_menu.common import fluent_icon, make_menu_action


@dataclass(frozen=True)
class FolderMenuActions:
    load_state: Callable[[], dict]
    create_folder: Callable[[str], object]
    rename_folder: Callable[[str, str], object]
    delete_folder: Callable[[str], object]
    move_folder_by_step: Callable[[str, int], object]
    set_folder_collapsed: Callable[[str, bool], object]
    reset_folders: Callable[[], object]


@dataclass(frozen=True)
class FolderMenuLabels:
    reset_title: str
    reset_body: str
    create_subtitle: str
    rename_subtitle: str
    delete_body: str
    action_error_suffix: str


class FolderNameDialog(MessageBoxBase):
    def __init__(self, *, title: str, subtitle: str, button_text: str, current_name: str = "", parent=None):
        if parent is not None and not parent.isWindow():
            parent = parent.window()
        super().__init__(parent)

        self.titleLabel = SubtitleLabel(title, self.widget)
        self.subtitleLabel = BodyLabel(subtitle, self.widget)
        self.subtitleLabel.setWordWrap(True)

        self.nameEdit = LineEdit(self.widget)
        self.nameEdit.setText(str(current_name or ""))
        self.nameEdit.setPlaceholderText("Название папки")
        self.nameEdit.setClearButtonEnabled(True)
        self.nameEdit.selectAll()

        self.warningLabel = CaptionLabel("", self.widget)
        style_semantic_caption_label(self.warningLabel, tone="error")
        self.warningLabel.hide()

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.subtitleLabel)
        self.viewLayout.addWidget(self.nameEdit)
        self.viewLayout.addWidget(self.warningLabel)

        self.yesButton.setText(button_text)
        self.cancelButton.setText("Отмена")
        self.widget.setMinimumWidth(420)

    def validate(self) -> bool:
        if self.nameEdit.text().strip():
            self.warningLabel.hide()
            return True
        self.warningLabel.setText("Введите название папки.")
        self.warningLabel.show()
        return False


def show_folder_context_menu(
    *,
    parent,
    folder_key: str,
    global_pos,
    actions: FolderMenuActions,
    labels: FolderMenuLabels,
    refresh_fn: Callable[[], object],
    log_fn: Callable[[str, str], object] | None = None,
    service_folder_keys: set[str] | None = None,
) -> None:
    key = str(folder_key or "").strip()
    service_keys = {str(value or "").strip() for value in (service_folder_keys or set()) if str(value or "").strip()}
    state = actions.load_state()
    folders = state.get("folders", {}) if isinstance(state, dict) else {}
    folder = folders.get(key) if isinstance(folders, dict) else None
    is_service = key in service_keys
    is_existing_folder = isinstance(folder, dict) or is_service
    is_system = bool(folder.get("system", False)) if isinstance(folder, dict) else is_service
    is_collapsed = bool(folder.get("collapsed", False)) if isinstance(folder, dict) else False

    menu = RoundMenu(parent=parent)

    if is_existing_folder:
        collapse_action = make_menu_action("Развернуть" if is_collapsed else "Свернуть", icon=fluent_icon("DOWN" if is_collapsed else "UP"), parent=menu)
        collapse_action.triggered.connect(
            lambda: _run_folder_action(
                parent,
                lambda: actions.set_folder_collapsed(key, not is_collapsed),
                refresh_fn,
                log_fn,
                f"не удалось свернуть или развернуть папку {labels.action_error_suffix}",
            )
        )
        menu.addAction(collapse_action)

    if is_service:
        menu.exec(global_pos)
        return

    if menu.actions():
        menu.addSeparator()
    create_action = make_menu_action("Создать папку", icon=fluent_icon("ADD"), parent=menu)
    create_action.triggered.connect(lambda: _create_folder(parent, actions, labels, refresh_fn, log_fn))
    menu.addAction(create_action)

    if is_existing_folder and not is_system:
        menu.addSeparator()
        rename_action = make_menu_action("Переименовать папку", icon=fluent_icon("EDIT"), parent=menu)
        rename_action.triggered.connect(
            lambda: _rename_folder(
                parent,
                actions,
                labels,
                key,
                str(folder.get("name") or ""),
                refresh_fn,
                log_fn,
            )
        )
        menu.addAction(rename_action)

        delete_action = make_menu_action("Удалить папку", icon=fluent_icon("DELETE"), parent=menu)
        delete_action.triggered.connect(lambda: _delete_folder(parent, actions, labels, key, refresh_fn, log_fn))
        menu.addAction(delete_action)

    if is_existing_folder:
        menu.addSeparator()
        move_up_action = make_menu_action("Переместить выше", icon=fluent_icon("UP"), parent=menu)
        move_down_action = make_menu_action("Переместить ниже", icon=fluent_icon("DOWN"), parent=menu)
        move_up_action.triggered.connect(
            lambda: _run_folder_action(
                parent,
                lambda: actions.move_folder_by_step(key, -1),
                refresh_fn,
                log_fn,
                f"не удалось переместить папку {labels.action_error_suffix}",
            )
        )
        move_down_action.triggered.connect(
            lambda: _run_folder_action(
                parent,
                lambda: actions.move_folder_by_step(key, 1),
                refresh_fn,
                log_fn,
                f"не удалось переместить папку {labels.action_error_suffix}",
            )
        )
        menu.addAction(move_up_action)
        menu.addAction(move_down_action)

    menu.addSeparator()
    reset_action = make_menu_action(labels.reset_title, icon=fluent_icon("SYNC"), parent=menu)
    reset_action.triggered.connect(lambda: _reset_folders(parent, actions, labels, refresh_fn, log_fn))
    menu.addAction(reset_action)

    menu.exec(global_pos)


def _create_folder(parent, actions: FolderMenuActions, labels: FolderMenuLabels, refresh_fn: Callable[[], object], log_fn) -> None:
    dialog = FolderNameDialog(
        title="Создать папку",
        subtitle=labels.create_subtitle,
        button_text="Создать",
        parent=parent,
    )
    if not dialog.exec():
        return
    name = dialog.nameEdit.text().strip()
    _run_folder_action(parent, lambda: bool(actions.create_folder(name)), refresh_fn, log_fn, f"не удалось создать папку {labels.action_error_suffix}")


def _rename_folder(parent, actions: FolderMenuActions, labels: FolderMenuLabels, folder_key: str, current_name: str, refresh_fn: Callable[[], object], log_fn) -> None:
    dialog = FolderNameDialog(
        title="Переименовать папку",
        subtitle=labels.rename_subtitle,
        button_text="Переименовать",
        current_name=current_name,
        parent=parent,
    )
    if not dialog.exec():
        return
    name = dialog.nameEdit.text().strip()
    _run_folder_action(parent, lambda: bool(actions.rename_folder(folder_key, name)), refresh_fn, log_fn, f"не удалось переименовать папку {labels.action_error_suffix}")


def _delete_folder(parent, actions: FolderMenuActions, labels: FolderMenuLabels, folder_key: str, refresh_fn: Callable[[], object], log_fn) -> None:
    box = MessageBox(
        "Удалить папку",
        labels.delete_body,
        parent.window() if parent is not None and not parent.isWindow() else parent,
    )
    box.yesButton.setText("Удалить")
    box.cancelButton.setText("Отмена")
    if not box.exec():
        return
    _run_folder_action(parent, lambda: bool(actions.delete_folder(folder_key)), refresh_fn, log_fn, f"не удалось удалить папку {labels.action_error_suffix}")


def _reset_folders(parent, actions: FolderMenuActions, labels: FolderMenuLabels, refresh_fn: Callable[[], object], log_fn) -> None:
    box = MessageBox(
        labels.reset_title,
        labels.reset_body,
        parent.window() if parent is not None and not parent.isWindow() else parent,
    )
    box.yesButton.setText("Сбросить")
    box.cancelButton.setText("Отмена")
    if not box.exec():
        return
    _run_folder_action(parent, lambda: bool(actions.reset_folders()), refresh_fn, log_fn, f"не удалось сбросить папки {labels.action_error_suffix}")


def _run_folder_action(parent, action: Callable[[], object], refresh_fn: Callable[[], object], log_fn, error_text: str) -> None:
    try:
        if action():
            refresh_fn()
    except Exception as exc:
        if log_fn is not None:
            log_fn(f"{parent.__class__.__name__}: {error_text}: {exc}", "ERROR")


__all__ = [
    "FolderMenuActions",
    "FolderMenuLabels",
    "FolderNameDialog",
    "show_folder_context_menu",
]
