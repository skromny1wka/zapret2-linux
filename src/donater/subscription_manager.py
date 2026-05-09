# donater/subscription_manager.py

from typing import Any, Dict, Optional

from PyQt6.QtCore import QThread, QObject, pyqtSignal
from donater.subscription_ui_applier import SubscriptionUiApplier
from log.log import log



class SubscriptionManager:
    """Запускает PremiumService в фоне и передаёт результат в UI-слой."""

    def __init__(self, app_instance):
        self.app = app_instance
        self.donate_checker = None
        self._subscription_thread: Optional[QThread] = None
        self._subscription_worker: Optional[QObject] = None
        self._cleanup_in_progress = False
        self._ui_applier = SubscriptionUiApplier(app_instance)

    @staticmethod
    def _shutdown_thread(thread: Optional[QThread], *, wait_timeout_ms: int = 2000) -> Optional[QThread]:
        if thread is None:
            return None
        try:
            if thread.isRunning():
                thread.quit()
                if not thread.wait(wait_timeout_ms):
                    log("⚠ Поток подписки не завершился, принудительно завершаем", "WARNING")
                    thread.terminate()
                    thread.wait(500)
        except RuntimeError:
            return None
        except Exception as e:
            log(f"Ошибка остановки потока подписки: {e}", "DEBUG")
        return None

    def initialize_async(self):
        """Асинхронная инициализация и проверка подписки"""
        self._cleanup_in_progress = False
        if self._subscription_thread is not None:
            try:
                if self._subscription_thread.isRunning():
                    log("Инициализация подписки уже выполняется, повторный запуск пропущен", "DEBUG")
                    return
            except RuntimeError:
                self._subscription_thread = None
                self._subscription_worker = None

        class SubscriptionInitWorker(QObject):
            finished = pyqtSignal(object, object, bool)  # donate_checker, activation_info, success
            progress = pyqtSignal(str)

            def run(self):
                try:
                    self.progress.emit("Инициализация системы подписок...")

                    # Создаем канонический PremiumService
                    from donater.service import get_premium_service
                    donate_checker = get_premium_service()

                    self.progress.emit("Проверка статуса подписки...")

                    # На старте используем кэш/оффлайн статус без сети,
                    # а сетевую проверку выполняем позже отложенным фоновым таском.
                    activation_info = donate_checker.check_device_activation(use_cache=True)

                    log(f"Статус подписки: {activation_info.get('status', 'unknown')}", "INFO")

                    self.finished.emit(donate_checker, activation_info, True)

                except Exception as e:
                    log(f"Ошибка инициализации подписок: {e}", "❌ ERROR")
                    import traceback
                    log(f"Traceback: {traceback.format_exc()}", "DEBUG")
                    self.finished.emit(None, None, False)

        # Показываем что идет загрузка
        self.app.set_status("Инициализация подписок...")

        self._subscription_thread = QThread(self.app)
        self._subscription_worker = SubscriptionInitWorker()
        self._subscription_worker.moveToThread(self._subscription_thread)

        def _cleanup_subscription_objects():
            self._subscription_worker = None
            self._subscription_thread = None

        self._subscription_thread.started.connect(self._subscription_worker.run)
        self._subscription_worker.progress.connect(self.app.set_status)
        self._subscription_worker.finished.connect(self._on_subscription_ready)
        self._subscription_worker.finished.connect(self._subscription_thread.quit)
        self._subscription_worker.finished.connect(self._subscription_worker.deleteLater)
        self._subscription_thread.finished.connect(self._subscription_thread.deleteLater)
        self._subscription_thread.finished.connect(_cleanup_subscription_objects)

        self._subscription_thread.start()

    @staticmethod
    def _build_subscription_info(activation_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        info = activation_info if isinstance(activation_info, dict) else {}
        is_premium = bool(info.get('activated') or info.get('is_premium'))
        days_remaining = info.get('days_remaining') if is_premium else None
        return {
            'is_premium': is_premium,
            'status_msg': str(info.get('status') or ('Premium активен' if is_premium else 'Не активировано')),
            'days_remaining': days_remaining,
            'subscription_level': str(info.get('subscription_level') or ('zapretik' if is_premium else '–')),
        }

    def _on_subscription_ready(self, donate_checker, activation_info, success):
        """✅ ОБНОВЛЕННЫЙ обработчик готовности подписки"""
        if self._cleanup_in_progress:
            return
        if not success or not donate_checker:
            log("PremiumService не инициализирован", "⚠ WARNING")
            self._ui_applier.apply_subscription_init_failed()
            return

        # Сохраняем checker
        self.donate_checker = donate_checker
        self.app.donate_checker = donate_checker

        # Используем результат воркера без повторного запроса к API в UI-потоке.
        try:
            sub_info = self._build_subscription_info(activation_info)

            log(f"Информация о подписке получена: premium={sub_info['is_premium']}, "
                f"days={sub_info['days_remaining']}, level={sub_info['subscription_level']}", "DEBUG")

        except Exception as e:
            log(f"Ошибка получения информации о подписке: {e}", "❌ ERROR")
            # Fallback значения
            sub_info = {
                'is_premium': False,
                'status_msg': 'Ошибка проверки',
                'days_remaining': None,
                'subscription_level': '–'
            }

        self._ui_applier.apply_subscription_info(sub_info)
        self._ui_applier.apply_subscription_ready()

        log(f"Подписка готова: {'Premium' if sub_info['is_premium'] else 'Free'} "
            f"(уровень: {sub_info['subscription_level']})", "INFO")

    def cleanup(self) -> None:
        """Останавливает фоновые потоки менеджера подписки при закрытии приложения."""
        self._cleanup_in_progress = True
        self._subscription_thread = self._shutdown_thread(self._subscription_thread)
        self._subscription_worker = None
