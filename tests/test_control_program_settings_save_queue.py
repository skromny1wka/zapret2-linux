from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock


class _SaveRuntime:
    def __init__(self, *, running: bool) -> None:
        self.running = bool(running)
        self.started: list[object] = []

    def is_running(self) -> bool:
        return self.running

    def start_qthread_worker(self, *, worker_factory, **_kwargs):
        worker = worker_factory(0)
        self.started.append(worker)
        return 0, worker


class _Page:
    from presets.ui.control.control_page_shared import ControlPageActionMixin

    _request_program_settings_save = ControlPageActionMixin._request_program_settings_save
    _on_program_settings_save_worker_finished = ControlPageActionMixin._on_program_settings_save_worker_finished
    create_program_settings_save_worker = Mock()
    _on_program_settings_save_finished = Mock()
    _on_program_settings_save_failed = Mock()
    _bind_program_settings_save_worker = Mock()


class ControlProgramSettingsSaveQueueTests(unittest.TestCase):
    def _make_page(self, *, running: bool):
        save_runtime = _SaveRuntime(running=running)
        page = _Page()
        page._cleanup_in_progress = False
        page._refresh_runtime = SimpleNamespace(
            program_settings_save_runtime=save_runtime,
            program_settings_save_pending=[],
        )
        page.create_program_settings_save_worker = Mock(return_value=object())
        page._on_program_settings_save_finished = Mock()
        page._on_program_settings_save_failed = Mock()
        page._bind_program_settings_save_worker = Mock()
        return page, save_runtime

    def test_program_settings_save_keeps_all_pending_actions(self) -> None:
        page, save_runtime = self._make_page(running=True)

        _Page._request_program_settings_save(page, "auto_dpi", True)
        _Page._request_program_settings_save(page, "hide_to_tray", False)

        self.assertEqual(save_runtime.started, [])
        self.assertEqual(
            page._refresh_runtime.program_settings_save_pending,
            [
                ("auto_dpi", True),
                ("hide_to_tray", False),
            ],
        )

    def test_program_settings_finished_starts_next_pending_save(self) -> None:
        page, save_runtime = self._make_page(running=False)
        worker = object()
        page.create_program_settings_save_worker = Mock(return_value=worker)
        page._refresh_runtime.program_settings_save_pending = [("hide_to_tray", True)]

        _Page._on_program_settings_save_worker_finished(page, object())

        page.create_program_settings_save_worker.assert_called_once_with(
            0,
            action="hide_to_tray",
            enabled=True,
        )
        self.assertEqual(save_runtime.started, [worker])
        self.assertEqual(page._refresh_runtime.program_settings_save_pending, [])


if __name__ == "__main__":
    unittest.main()
