from __future__ import annotations

import unittest
from types import SimpleNamespace


class InternetCleanupTests(unittest.TestCase):
    def test_reset_command_plan_uses_system_executables_without_cmd_shell(self) -> None:
        from windows_features.internet_cleanup import build_internet_cleanup_commands

        commands = build_internet_cleanup_commands(
            resolve_system_exe=lambda name: f"C:/Windows/System32/{name}",
        )

        args_list = [command.args for command in commands]
        self.assertEqual(
            args_list,
            [
                ("C:/Windows/System32/netsh.exe", "int", "ip", "reset"),
                ("C:/Windows/System32/netsh.exe", "winhttp", "reset", "proxy"),
                ("C:/Windows/System32/netsh.exe", "winsock", "reset"),
                ("C:/Windows/System32/netsh.exe", "interface", "ipv4", "reset"),
                ("C:/Windows/System32/netsh.exe", "interface", "ipv6", "reset"),
                (
                    "C:/Windows/System32/netsh.exe",
                    "int",
                    "ipv4",
                    "set",
                    "dynamicport",
                    "tcp",
                    "start=10000",
                    "num=30000",
                ),
            ],
        )
        self.assertFalse(any("cmd.exe" in part.lower() for args in args_list for part in args))
        self.assertTrue(all(command.timeout_seconds > 0 for command in commands))

    def test_run_internet_cleanup_reports_success_and_uses_native_dns_flush(self) -> None:
        from windows_features.internet_cleanup import run_internet_cleanup

        calls: list[tuple[str, ...]] = []
        statuses: list[str] = []
        dns_flush_calls: list[bool] = []

        def command_runner(args, **_kwargs):
            calls.append(tuple(args))
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        result = run_internet_cleanup(
            command_runner=command_runner,
            flush_dns_cache=lambda: dns_flush_calls.append(True) or True,
            status_callback=statuses.append,
            resolve_system_exe=lambda name: f"C:/Windows/System32/{name}",
        )

        self.assertEqual(result.level, "success")
        self.assertIn("перезагруз", result.content.lower())
        self.assertEqual(len(calls), 6)
        self.assertEqual(dns_flush_calls, [True])
        self.assertTrue(statuses[0].startswith("Сброс TCP/IP"))

    def test_internet_cleanup_confirmation_plan_warns_about_reboot(self) -> None:
        import presets.ui.control.control_runtime as control_runtime

        plan = control_runtime.build_internet_cleanup_start_plan(language="ru")

        self.assertFalse(plan.blocked)
        self.assertEqual(plan.start_status, "Сброс сети Windows...")
        self.assertEqual(len(plan.confirmations), 1)
        self.assertIn("перезагрузка", plan.confirmations[0].content.lower())


if __name__ == "__main__":
    unittest.main()
