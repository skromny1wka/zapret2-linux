"""Диалог добавления или редактирования одного пользовательского DNS."""

from __future__ import annotations

from ipaddress import IPv4Address
from uuid import uuid4

from qfluentwidgets import BodyLabel, CaptionLabel, LineEdit, MessageBoxBase, SubtitleLabel

from ui.accessibility import remove_line_edit_buttons_from_tab_order, set_control_accessibility, set_state_text
from ui.fluent_widgets import style_semantic_caption_label


class CustomDnsDialog(MessageBoxBase):
    """Окно для одного DNS: создать новый или изменить выбранный."""

    def __init__(self, parent=None, *, server: dict | None = None):
        if parent is not None and not parent.isWindow():
            parent = parent.window()
        super().__init__(parent)
        self._server = _copy_server(server or {})
        self._server_id = str(self._server.get("id") or "")

        editing = bool(self._server_id)
        self.titleLabel = SubtitleLabel("Редактировать свой DNS" if editing else "Добавить свой DNS", self.widget)
        self.subtitleLabel = BodyLabel(
            "Укажите DNS-сервер. После сохранения он появится в общем списке DNS.",
            self.widget,
        )
        self.subtitleLabel.setWordWrap(True)

        self.nameEdit = LineEdit(self.widget)
        self.nameEdit.setPlaceholderText("Название, например Мой DNS")
        self.nameEdit.setClearButtonEnabled(True)

        self.primaryEdit = LineEdit(self.widget)
        self.primaryEdit.setPlaceholderText("Основной DNS, например 8.8.8.8")
        self.primaryEdit.setClearButtonEnabled(True)

        self.secondaryEdit = LineEdit(self.widget)
        self.secondaryEdit.setPlaceholderText("Дополнительный DNS, например 1.1.1.1")
        self.secondaryEdit.setClearButtonEnabled(True)

        ipv4 = list(self._server.get("ipv4", []) or [])
        self.nameEdit.setText(str(self._server.get("name") or ""))
        self.primaryEdit.setText(str(ipv4[0] if ipv4 else ""))
        self.secondaryEdit.setText(str(ipv4[1] if len(ipv4) > 1 else ""))

        self.warningLabel = CaptionLabel("", self.widget)
        style_semantic_caption_label(self.warningLabel, tone="error")
        self.warningLabel.hide()

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.subtitleLabel)
        self.viewLayout.addWidget(BodyLabel("Название", self.widget))
        self.viewLayout.addWidget(self.nameEdit)
        self.viewLayout.addWidget(BodyLabel("Основной DNS", self.widget))
        self.viewLayout.addWidget(self.primaryEdit)
        self.viewLayout.addWidget(BodyLabel("Дополнительный DNS", self.widget))
        self.viewLayout.addWidget(self.secondaryEdit)
        self.viewLayout.addWidget(self.warningLabel)

        self.yesButton.setText("Сохранить" if editing else "Добавить")
        self.cancelButton.setText("Отмена")
        self.widget.setMinimumWidth(520)
        self._install_accessibility(editing=editing)

    def server(self) -> dict:
        return _copy_server(self._server)

    def servers(self) -> list[dict]:
        server = self.server()
        return [server] if server.get("id") else []

    def validate(self) -> bool:
        name = self.nameEdit.text().strip()
        primary = self.primaryEdit.text().strip()
        secondary = self.secondaryEdit.text().strip()
        if not name:
            self._show_warning("Введите название DNS.")
            return False
        if not primary:
            self._show_warning("Введите основной DNS сервер.")
            return False
        if not _is_ipv4(primary):
            self._show_warning("Основной DNS должен быть IPv4 адресом.")
            return False
        if secondary and not _is_ipv4(secondary):
            self._show_warning("Дополнительный DNS должен быть IPv4 адресом.")
            return False

        self._server = {
            "id": self._server_id or f"custom-{uuid4().hex[:12]}",
            "name": name,
            "ipv4": [primary] + ([secondary] if secondary else []),
            "ipv6": [],
        }
        self._server_id = str(self._server["id"])
        self.warningLabel.hide()
        return True

    def _install_accessibility(self, *, editing: bool) -> None:
        set_control_accessibility(
            self.nameEdit,
            name="Название своего DNS",
            description="Введите понятное имя, которое будет показано в списке DNS.",
        )
        remove_line_edit_buttons_from_tab_order(self.nameEdit)
        set_control_accessibility(
            self.primaryEdit,
            name="Основной DNS сервер",
            description="Введите первый DNS сервер. Например 8.8.8.8.",
        )
        remove_line_edit_buttons_from_tab_order(self.primaryEdit)
        set_control_accessibility(
            self.secondaryEdit,
            name="Дополнительный DNS сервер",
            description="Введите второй DNS сервер, если он нужен.",
        )
        remove_line_edit_buttons_from_tab_order(self.secondaryEdit)

        action_text = "Сохранить свой DNS" if editing else "Добавить свой DNS"
        set_state_text(self.yesButton, action_text)
        set_control_accessibility(
            self.yesButton,
            name=action_text,
            description="Сохраняет DNS и закрывает окно.",
        )
        set_state_text(self.cancelButton, "Отменить изменение своего DNS")
        set_control_accessibility(
            self.cancelButton,
            name="Отменить изменение своего DNS",
            description="Закрывает окно без применения изменений.",
        )

    def _show_warning(self, text: str) -> None:
        self.warningLabel.setText(text)
        self.warningLabel.show()
        set_state_text(self.warningLabel, f"Ошибка: {text}")


def _copy_server(server: dict) -> dict:
    return {
        "id": str(server.get("id") or ""),
        "name": str(server.get("name") or ""),
        "ipv4": [str(item) for item in server.get("ipv4", []) or []],
        "ipv6": [str(item) for item in server.get("ipv6", []) or []],
    }


def is_ipv4(value: str) -> bool:
    return _is_ipv4(value)


def unique_copy_name(base_name: str, existing_names: list[str]) -> str:
    base = str(base_name or "Свой DNS").strip() or "Свой DNS"
    existing = {str(name or "").strip().lower() for name in existing_names}
    first = f"{base} копия"
    if first.lower() not in existing:
        return first
    index = 2
    while True:
        candidate = f"{first} {index}"
        if candidate.lower() not in existing:
            return candidate
        index += 1


def _is_ipv4(value: str) -> bool:
    try:
        IPv4Address(str(value).strip())
    except Exception:
        return False
    return True


__all__ = ["CustomDnsDialog", "is_ipv4", "unique_copy_name"]
