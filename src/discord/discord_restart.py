# discord_restart.py

from PyQt6.QtWidgets import QMessageBox
from settings.store import get_discord_restart_enabled, set_discord_restart_enabled

# ----------------------------------------------------------------------
# 1.  Чтение / запись настройки в реестре
# ----------------------------------------------------------------------
def get_discord_restart_setting(default: bool = True) -> bool:
    """
    Возвращает текущее значение AutoRestartDiscord.
    Если параметра нет – отдаёт default (по-умолчанию True).
    """
    try:
        return bool(get_discord_restart_enabled())
    except Exception:
        return bool(default)


def set_discord_restart_setting(enabled: bool) -> bool:
    """
    Записывает AutoRestartDiscord = 1/0.
    Возвращает True при успехе.
    """
    return bool(set_discord_restart_enabled(bool(enabled)))


# ----------------------------------------------------------------------
# 2.  UI-переключатель
# ----------------------------------------------------------------------
def toggle_discord_restart(
        status_callback=None,
    ) -> bool:
    """
    Переключает настройку автоперезапуска Discord, показывая диалоги
    подтверждения/информирования.

    status_callback(msg) – функция вывода статуса (можно None)
    """
    current = get_discord_restart_setting()

    # ----- хотим ОТКЛЮЧИТЬ ------------------------------------------------
    if current:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Отключение автоперезапуска Discord")
        msg.setText("Вы действительно хотите отключить автоматический "
                    "перезапуск Discord?")
        msg.setInformativeText(
            "После отключения вам придётся вручную перезапускать Discord "
            "при смене стратегии, иначе возможны проблемы со связью."
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if msg.exec() != QMessageBox.StandardButton.Yes:
            return False   # пользователь отменил

        set_discord_restart_setting(False)

        if status_callback:
            status_callback("Автоматический перезапуск Discord отключён")

        QMessageBox.information(None, "Настройка изменена",
                                "Автоматический перезапуск Discord отключён.\n\n"
                                "При смене стратегии перезапускайте Discord вручную.")
        return True

    # ----- хотим ВКЛЮЧИТЬ -------------------------------------------------
    set_discord_restart_setting(True)

    if status_callback:
        status_callback("Автоматический перезапуск Discord включён")

    QMessageBox.information(None, "Настройка изменена",
                            "Автоматический перезапуск Discord снова включён.")
    return True
