from __future__ import annotations

from log.log import log
from profile.ui.profile_order_list import ProfileOrderList
from qfluentwidgets import BodyLabel, BreadcrumbBar, InfoBar
from settings.mode import ZAPRET1_MODE, ZAPRET2_MODE
from ui.pages.base_page import BasePage
from app.ui_texts import tr as tr_catalog


class ProfileOrderPageBase(BasePage):
    launch_method = ZAPRET2_MODE
    title_key = "page.winws2_profile_order.title"
    control_key = "page.winws2_profile_setup.breadcrumb.control"
    profiles_key = "page.winws2_pages.title"
    profiles_default = "Настройка пресета"

    def __init__(self, parent=None, *, profile_feature, open_profiles, open_root):
        super().__init__(
            title="Порядок в preset",
            parent=parent,
            title_key=self.title_key,
        )
        self._profile = profile_feature
        self._open_profiles = open_profiles
        self._open_root = open_root
        self._payload = None
        self._order_list: ProfileOrderList | None = None
        self._breadcrumb = None
        self._build_content()

    def on_page_activated(self) -> None:
        self._reload_order_profiles()

    def _build_content(self) -> None:
        if self.title_label is not None:
            self.title_label.hide()
        if self.subtitle_label is not None:
            self.subtitle_label.hide()

        self._breadcrumb = BreadcrumbBar(self)
        self._breadcrumb.currentItemChanged.connect(self._on_breadcrumb_item_changed)
        self.layout.addWidget(self._breadcrumb)

        hint = BodyLabel(
            "Profile выше в списке имеет больший приоритет. "
            "Если два profile-а подходят к одному домену или IP, будет применён тот, который находится выше."
        )
        hint.setWordWrap(True)
        self.layout.addWidget(hint)

        self._order_list = ProfileOrderList(self)
        self._order_list.profile_move_requested.connect(self._on_profile_move_requested)
        self._order_list.profile_move_after_requested.connect(self._on_profile_move_after_requested)
        self._order_list.profile_move_to_end_requested.connect(self._on_profile_move_to_end_requested)
        self.layout.addWidget(self._order_list, 1)
        self._rebuild_breadcrumb()

    def _reload_order_profiles(self) -> None:
        try:
            payload = self._profile.list_preset_order_profiles(self.launch_method)
            self._payload = payload
            if self._order_list is not None:
                self._order_list.set_profiles(tuple(getattr(payload, "items", ()) or ()))
            self._rebuild_breadcrumb()
        except Exception as exc:
            log(f"{self.__class__.__name__}: не удалось прочитать порядок profile-ов: {exc}", "ERROR")
            InfoBar.error(title="Ошибка", content=str(exc), parent=self.window())

    def _on_profile_move_requested(self, source_profile_key: str, destination_profile_key: str) -> None:
        try:
            moved = self._profile.move_preset_profile_before(
                self.launch_method,
                source_profile_key,
                destination_profile_key,
            )
            if moved:
                self._reload_order_profiles()
        except Exception as exc:
            log(f"{self.__class__.__name__}: не удалось переместить profile выше: {exc}", "ERROR")
            InfoBar.error(title="Ошибка", content=str(exc), parent=self.window())

    def _on_profile_move_after_requested(self, source_profile_key: str, destination_profile_key: str) -> None:
        try:
            moved = self._profile.move_preset_profile_after(
                self.launch_method,
                source_profile_key,
                destination_profile_key,
            )
            if moved:
                self._reload_order_profiles()
        except Exception as exc:
            log(f"{self.__class__.__name__}: не удалось переместить profile ниже: {exc}", "ERROR")
            InfoBar.error(title="Ошибка", content=str(exc), parent=self.window())

    def _on_profile_move_to_end_requested(self, profile_key: str) -> None:
        try:
            moved = self._profile.move_preset_profile_to_end(self.launch_method, profile_key)
            if moved:
                self._reload_order_profiles()
        except Exception as exc:
            log(f"{self.__class__.__name__}: не удалось переместить profile в конец: {exc}", "ERROR")
            InfoBar.error(title="Ошибка", content=str(exc), parent=self.window())

    def _rebuild_breadcrumb(self) -> None:
        if self._breadcrumb is None:
            return
        self._breadcrumb.blockSignals(True)
        try:
            self._breadcrumb.clear()
            self._breadcrumb.addItem("control", tr_catalog(self.control_key, language=self._ui_language, default="Управление"))
            self._breadcrumb.addItem("profiles", tr_catalog(self.profiles_key, language=self._ui_language, default=self.profiles_default))
            self._breadcrumb.addItem("order", "Порядок в preset")
        finally:
            self._breadcrumb.blockSignals(False)

    def _on_breadcrumb_item_changed(self, key: str) -> None:
        if key == "control":
            self._open_root()
        elif key == "profiles":
            self._open_profiles()
        elif key == "order":
            self._rebuild_breadcrumb()


class Zapret2ProfileOrderPage(ProfileOrderPageBase):
    launch_method = ZAPRET2_MODE
    title_key = "page.winws2_profile_order.title"
    control_key = "page.winws2_profile_setup.breadcrumb.control"
    profiles_key = "page.winws2_pages.title"
    profiles_default = "Настройка пресета"


class Zapret1ProfileOrderPage(ProfileOrderPageBase):
    launch_method = ZAPRET1_MODE
    title_key = "page.winws1_profile_order.title"
    control_key = "page.winws1_profile_setup.breadcrumb.control"
    profiles_key = "page.winws1_pages.title"
    profiles_default = "Настройка пресета"


__all__ = ["ProfileOrderPageBase", "Zapret1ProfileOrderPage", "Zapret2ProfileOrderPage"]
