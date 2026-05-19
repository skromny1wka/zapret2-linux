from __future__ import annotations

from qfluentwidgets import BodyLabel, CaptionLabel, ComboBox, LineEdit, MessageBoxBase, SubtitleLabel

from ui.fluent_widgets import style_semantic_caption_label


class CreateUserProfileDialog(MessageBoxBase):
    def __init__(self, parent=None):
        if parent is not None and not parent.isWindow():
            parent = parent.window()
        super().__init__(parent)

        self.titleLabel = SubtitleLabel("Добавить profile", self.widget)
        self.subtitleLabel = BodyLabel(
            "Создаёт пользовательский profile и два пустых файла списка: hostlist и ipset.",
            self.widget,
        )
        self.subtitleLabel.setWordWrap(True)

        self.nameEdit = LineEdit(self.widget)
        self.nameEdit.setPlaceholderText("Название profile")
        self.nameEdit.setClearButtonEnabled(True)

        self.protocolCombo = ComboBox(self.widget)
        self.protocolCombo.addItem("TCP", userData="tcp")
        self.protocolCombo.addItem("UDP", userData="udp")

        self.portsEdit = LineEdit(self.widget)
        self.portsEdit.setPlaceholderText("Порты, например 80,443")
        self.portsEdit.setClearButtonEnabled(True)

        self.warningLabel = CaptionLabel("", self.widget)
        style_semantic_caption_label(self.warningLabel, tone="error")
        self.warningLabel.hide()

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.subtitleLabel)
        self.viewLayout.addWidget(BodyLabel("Название", self.widget))
        self.viewLayout.addWidget(self.nameEdit)
        self.viewLayout.addWidget(BodyLabel("Тип", self.widget))
        self.viewLayout.addWidget(self.protocolCombo)
        self.viewLayout.addWidget(BodyLabel("Порты", self.widget))
        self.viewLayout.addWidget(self.portsEdit)
        self.viewLayout.addWidget(self.warningLabel)

        self.yesButton.setText("Добавить")
        self.cancelButton.setText("Отмена")
        self.widget.setMinimumWidth(440)
        self.nameEdit.returnPressed.connect(self._validate_and_accept)
        self.portsEdit.returnPressed.connect(self._validate_and_accept)

    def values(self) -> tuple[str, str, str]:
        protocol = str(self.protocolCombo.itemData(self.protocolCombo.currentIndex()) or "tcp")
        return self.nameEdit.text().strip(), protocol, self.portsEdit.text().strip()

    def validate(self) -> bool:
        name, _protocol, ports = self.values()
        if not name:
            self._show_warning("Введите название profile.")
            return False
        if not ports:
            self._show_warning("Введите порты.")
            return False
        self.warningLabel.hide()
        return True

    def _validate_and_accept(self) -> None:
        if self.validate():
            self.accept()

    def _show_warning(self, text: str) -> None:
        self.warningLabel.setText(text)
        self.warningLabel.show()
