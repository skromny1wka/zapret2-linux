from __future__ import annotations

import unittest

from PyQt6.QtCore import QCoreApplication


class IPCManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = QCoreApplication.instance() or QCoreApplication([])

    def test_dispatches_show_and_exit_commands(self) -> None:
        from startup.ipc_manager import (
            IPC_COMMAND_EXIT_KEEP_DPI,
            IPC_COMMAND_EXIT_STOP_DPI,
            IPC_COMMAND_SHOW_WINDOW,
            IPCManager,
        )

        manager = IPCManager()
        received: list[str] = []
        manager.show_window_signal.connect(lambda: received.append("show"))
        manager.exit_keep_dpi_signal.connect(lambda: received.append("exit_keep"))
        manager.exit_stop_dpi_signal.connect(lambda: received.append("exit_stop"))

        self.assertTrue(manager._dispatch_command(IPC_COMMAND_SHOW_WINDOW))
        self.assertTrue(manager._dispatch_command(IPC_COMMAND_EXIT_KEEP_DPI))
        self.assertTrue(manager._dispatch_command(IPC_COMMAND_EXIT_STOP_DPI))
        self.assertFalse(manager._dispatch_command("UNKNOWN"))
        self.assertEqual(received, ["show", "exit_keep", "exit_stop"])

    def test_exit_request_uses_window_lifecycle(self) -> None:
        from startup.ipc_manager import IPCManager

        class Window:
            def __init__(self) -> None:
                self.requests: list[bool] = []

            def request_exit(self, stop_dpi: bool) -> None:
                self.requests.append(bool(stop_dpi))

        window = Window()
        manager = IPCManager()
        manager.window = window

        manager._handle_exit_request(stop_dpi=False)
        manager._handle_exit_request(stop_dpi=True)

        self.assertEqual(window.requests, [False, True])

    def test_send_exit_command_uses_expected_wire_command(self) -> None:
        from startup.ipc_manager import (
            IPC_COMMAND_EXIT_KEEP_DPI,
            IPC_COMMAND_EXIT_STOP_DPI,
            IPCManager,
        )

        manager = IPCManager()
        sent: list[str] = []
        manager.send_command = lambda command: sent.append(command) or True

        self.assertTrue(manager.send_exit_command())
        self.assertTrue(manager.send_exit_command(stop_dpi=True))

        self.assertEqual(sent, [IPC_COMMAND_EXIT_KEEP_DPI, IPC_COMMAND_EXIT_STOP_DPI])


if __name__ == "__main__":
    unittest.main()
