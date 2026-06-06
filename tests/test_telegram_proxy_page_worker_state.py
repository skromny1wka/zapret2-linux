from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from telegram_proxy.ui.worker_state import TelegramProxyPageWorkerState


class TelegramProxyPageWorkerStateTests(unittest.TestCase):
    def test_request_marks_pending_when_runtime_is_busy(self) -> None:
        state = TelegramProxyPageWorkerState(
            runtime=SimpleNamespace(is_running=Mock(return_value=True)),
        )
        start = Mock()

        started = state.start_or_mark_pending(start)

        self.assertFalse(started)
        self.assertTrue(state.pending)
        start.assert_not_called()

    def test_schedule_keeps_one_pending_request_until_timer_runs(self) -> None:
        state = TelegramProxyPageWorkerState(
            runtime=SimpleNamespace(is_running=Mock(return_value=False)),
        )
        single_shot = Mock(side_effect=lambda _delay, _callback: None)
        start = Mock()

        state.schedule_next(single_shot, start)
        state.schedule_next(single_shot, start)

        single_shot.assert_called_once()
        self.assertTrue(state.pending)
        start.assert_not_called()

        single_shot.call_args.args[1]()

        start.assert_called_once_with()
        self.assertFalse(state.pending)
        self.assertFalse(state.start_scheduled)

    def test_stale_finish_does_not_schedule_pending_request(self) -> None:
        current_worker = SimpleNamespace()
        state = TelegramProxyPageWorkerState(
            runtime=SimpleNamespace(worker=current_worker),
            pending=True,
        )
        schedule_next = Mock()

        state.schedule_after_finish(
            SimpleNamespace(),
            is_current_worker_finish=lambda _runtime, worker: worker is current_worker,
            schedule_next=schedule_next,
        )

        schedule_next.assert_not_called()
        self.assertTrue(state.pending)


if __name__ == "__main__":
    unittest.main()
