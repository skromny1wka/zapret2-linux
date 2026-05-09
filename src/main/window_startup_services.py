from __future__ import annotations

import time

from log.log import log


def init_theme_manager(app) -> None:
    started_at = time.perf_counter()

    from config.config import THEME_FOLDER
    from PyQt6.QtWidgets import QApplication
    from ui.theme import ThemeManager

    app.theme_manager = ThemeManager(
        app=QApplication.instance(),
        widget=app,
        theme_folder=THEME_FOLDER,
        donate_checker=getattr(app, "donate_checker", None),
        apply_on_init=False,
    )

    current_theme = app.theme_manager.current_theme
    is_premium = False
    donate_checker = getattr(app, "donate_checker", None)
    if donate_checker is not None:
        try:
            sub_info = donate_checker.get_full_subscription_info(use_cache=True)
            is_premium = bool(sub_info.get("is_premium"))
        except Exception as exc:
            log(f"Не удалось прочитать premium-статус для темы: {exc}", "DEBUG")
    log(f"🎨 Тема инициализирована: '{current_theme}' (premium={is_premium})", "DEBUG")

    # qfluentwidgets управляет темой сам. Старый qt-material CSS здесь не нужен:
    # он может оставить тёмные цвета текста после переключения на светлую тему.
    log("⏭️ Применение CSS пропущено — qfluentwidgets управляет стилями нативно", "DEBUG")

    log(f"✅ Theme manager: {(time.perf_counter() - started_at) * 1000:.0f}ms (CSS в фоне)", "DEBUG")
