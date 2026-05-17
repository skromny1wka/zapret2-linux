from __future__ import annotations

from PyQt6.QtCore import QEvent, QTimer
from PyQt6.QtWidgets import QWidget

from log.log import log

from main.window_lifecycle_cleanup import (
    release_input_interaction_states,
)
from main.runtime_state import (
    log_startup_metric as emit_startup_metric,
    startup_elapsed_ms,
)
from ui.window_adapter import sync_titlebar_search_width


class WindowLifecycleMixin:
    def closeEvent(self, event):
        """Обрабатывает событие закрытия окна."""
        if not self.window_close_flow.should_continue_final_close(event):
            return

        self.close_state.is_exiting = True
        self.application_lifecycle.run_final_close_cleanup()

        super().closeEvent(event)

    def release_input_interaction_states(self) -> None:
        release_input_interaction_states(self)

    def request_exit(self, stop_dpi: bool) -> None:
        """Общий вход для tray и adapter-слоя."""
        self.application_lifecycle.request_exit(stop_dpi=bool(stop_dpi))

    def exit_keep_dpi(self) -> None:
        """Полный выход из GUI без остановки DPI."""
        self.application_lifecycle.exit_keep_dpi()

    def exit_stop_dpi(self) -> None:
        """Полный выход из GUI с остановкой DPI."""
        self.application_lifecycle.exit_stop_dpi()

    def close_to_tray(self) -> bool:
        """Скрывает окно в трей (без выхода из GUI)."""
        return self.application_lifecycle.close_to_tray()

    def changeEvent(self, event):
        if event.type() == QEvent.Type.ActivationChange:
            try:
                if not self.isActiveWindow():
                    self.release_input_interaction_states()
            except Exception as e:
                log(f"Не удалось сбросить состояние ввода при смене активности окна: {e}", "DEBUG")

        if event.type() == QEvent.Type.WindowStateChange:
            self.window_geometry_runtime.on_window_state_change()

            try:
                effects = self.visual_state.holiday_effects
                if effects is not None:
                    QTimer.singleShot(0, effects.sync_geometry)
            except Exception as e:
                log(f"Не удалось синхронизировать визуальные эффекты при смене состояния окна: {e}", "DEBUG")

        super().changeEvent(event)

    def hideEvent(self, event):
        try:
            self.release_input_interaction_states()
        except Exception as e:
            log(f"Не удалось сбросить состояние ввода при скрытии окна: {e}", "DEBUG")
        super().hideEvent(event)

    def moveEvent(self, event):
        super().moveEvent(event)
        self.window_geometry_runtime.on_geometry_changed()

    def resizeEvent(self, event):
        """Обновляем геометрию при изменении размера окна."""
        super().resizeEvent(event)
        try:
            sync_titlebar_search_width(self)
        except Exception as e:
            log(f"Не удалось синхронизировать ширину поиска в заголовке: {e}", "DEBUG")
        self.window_geometry_runtime.on_geometry_changed()
        try:
            effects = self.visual_state.holiday_effects
            if effects is not None:
                effects.sync_geometry()
        except Exception as e:
            log(f"Не удалось синхронизировать визуальные эффекты при изменении размера окна: {e}", "DEBUG")

    def showEvent(self, event):
        """Первый показ окна."""
        super().showEvent(event)

        startup_state = self.startup_state
        if not startup_state.ttff_logged:
            startup_state.ttff_logged = True
            startup_state.ttff_ms = startup_elapsed_ms()
            emit_startup_metric("StartupTTFF", "first showEvent")

        self.window_geometry_runtime.apply_saved_maximized_state_if_needed()
        QTimer.singleShot(350, self.window_geometry_runtime.enable_persistence)

        try:
            effects = self.visual_state.holiday_effects
            if effects is not None:
                effects.sync_geometry()
                QTimer.singleShot(0, effects.sync_geometry)
        except Exception as e:
            log(f"Не удалось синхронизировать визуальные эффекты при показе окна: {e}", "DEBUG")

        self.window_notification_center.schedule_startup_notification_queue(0)

    def _force_style_refresh(self) -> None:
        """Принудительно обновляет стили всех виджетов после показа окна."""
        try:
            for widget in self.findChildren(QWidget):
                widget.style().unpolish(widget)
                widget.style().polish(widget)

            log("🎨 Принудительное обновление стилей выполнено после показа окна", "DEBUG")
        except Exception as e:
            log(f"Ошибка обновления стилей: {e}", "DEBUG")
