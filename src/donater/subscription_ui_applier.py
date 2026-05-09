from __future__ import annotations

from typing import Any, Dict, Optional

from log.log import log


class SubscriptionUiApplier:
    """Применяет Premium-статус к главному окну."""

    def __init__(self, app_instance):
        self.app = app_instance

    def apply_subscription_info(
        self,
        sub_info: Dict[str, Any],
        *,
        status_message: Optional[str] = None,
    ) -> None:
        is_premium = bool(sub_info.get("is_premium"))
        days_remaining = sub_info.get("days_remaining")

        self.app.ui_state_store.set_subscription(is_premium, days_remaining)

        self.app.update_title_with_subscription_status(
            is_premium,
            self.app.theme_manager.current_theme,
            days_remaining,
        )
        log(f"Обновлён заголовок подписки: premium={is_premium}", "DEBUG")

        if status_message:
            self.app.set_status(status_message)

    def apply_subscription_init_failed(self) -> None:
        self.app.update_title_with_subscription_status(False, None, 0)
        self.app.set_status("Ошибка инициализации подписок")
        self.mark_startup_subscription_ready("subscription_init_failed")

    def apply_subscription_ready(self) -> None:
        self.app._init_garland_from_registry()
        self.app.set_status("Подписка инициализирована")
        self.mark_startup_subscription_ready("subscription_ready")

    def mark_startup_subscription_ready(self, source: str) -> None:
        try:
            self.app._mark_startup_subscription_ready(source)
        except Exception:
            pass
