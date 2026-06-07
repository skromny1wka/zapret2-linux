from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from PyQt6.QtCore import QThread, pyqtSignal

from log.log import log
from utils.subproc import get_system_exe, run_hidden


@dataclass(frozen=True, slots=True)
class InternetCleanupCommand:
    label: str
    args: tuple[str, ...]
    timeout_seconds: int = 45


@dataclass(slots=True)
class InternetCleanupActionResult:
    level: str
    title: str
    content: str
    revert_checked: bool | None
    final_status: str


def build_internet_cleanup_commands(
    *,
    resolve_system_exe: Callable[[str], str] = get_system_exe,
) -> tuple[InternetCleanupCommand, ...]:
    netsh = resolve_system_exe("netsh.exe")
    return (
        InternetCleanupCommand("Сброс TCP/IP", (netsh, "int", "ip", "reset")),
        InternetCleanupCommand("Сброс WinHTTP proxy", (netsh, "winhttp", "reset", "proxy")),
        InternetCleanupCommand("Сброс Winsock", (netsh, "winsock", "reset")),
        InternetCleanupCommand("Сброс IPv4", (netsh, "interface", "ipv4", "reset")),
        InternetCleanupCommand("Сброс IPv6", (netsh, "interface", "ipv6", "reset")),
        InternetCleanupCommand(
            "Настройка динамических TCP-портов",
            (
                netsh,
                "int",
                "ipv4",
                "set",
                "dynamicport",
                "tcp",
                "start=10000",
                "num=30000",
            ),
        ),
    )


def _flush_dns_cache_native() -> bool:
    try:
        from dns.dns_core import flush_dns_cache_native

        return bool(flush_dns_cache_native())
    except Exception as exc:
        log(f"Не удалось очистить DNS-кэш через WinAPI: {exc}", "DEBUG")
        return False


def _default_command_runner(args: Sequence[str], *, timeout: int):
    return run_hidden(
        tuple(args),
        wait=True,
        capture_output=True,
        timeout=timeout,
        shell=False,
    )


def _short_error_from_completed(completed: Any) -> str:
    stderr = str(getattr(completed, "stderr", "") or "").strip()
    stdout = str(getattr(completed, "stdout", "") or "").strip()
    text = stderr or stdout
    first_line = text.splitlines()[0].strip() if text else ""
    if len(first_line) <= 180:
        return first_line
    return first_line[:177] + "..."


def build_internet_cleanup_error_result(error: str) -> InternetCleanupActionResult:
    return InternetCleanupActionResult(
        level="error",
        title="Сброс сети не выполнен",
        content=str(error or "Не удалось выполнить очистку сети Windows."),
        revert_checked=None,
        final_status="",
    )


def run_internet_cleanup(
    *,
    command_runner: Callable[..., Any] | None = None,
    flush_dns_cache: Callable[[], bool] | None = None,
    status_callback: Callable[[str], None] | None = None,
    resolve_system_exe: Callable[[str], str] = get_system_exe,
) -> InternetCleanupActionResult:
    runner = command_runner or _default_command_runner
    flush_dns = flush_dns_cache or _flush_dns_cache_native
    commands = build_internet_cleanup_commands(resolve_system_exe=resolve_system_exe)

    failed: list[str] = []
    completed_count = 0
    for command in commands:
        if status_callback is not None:
            status_callback(f"{command.label}...")
        try:
            completed = runner(command.args, timeout=command.timeout_seconds)
        except Exception as exc:
            failed.append(f"{command.label}: {exc}")
            continue

        return_code = int(getattr(completed, "returncode", 1) or 0)
        if return_code == 0:
            completed_count += 1
            continue
        detail = _short_error_from_completed(completed)
        failed.append(f"{command.label}: код {return_code}" + (f", {detail}" if detail else ""))

    if status_callback is not None:
        status_callback("Очистка DNS-кэша...")
    dns_ok = bool(flush_dns())
    if dns_ok:
        completed_count += 1
    else:
        failed.append("Очистка DNS-кэша: не выполнена")

    if not failed:
        return InternetCleanupActionResult(
            level="success",
            title="Сеть Windows сброшена",
            content=(
                "Очистка выполнена. Если интернет не восстановится сразу, "
                "перезагрузите Windows."
            ),
            revert_checked=None,
            final_status="Готово",
        )

    if completed_count > 0:
        return InternetCleanupActionResult(
            level="warning",
            title="Сеть сброшена частично",
            content=(
                "Часть действий выполнена, но есть ошибки:\n"
                + "\n".join(failed[:4])
                + "\n\nПосле этого всё равно может понадобиться перезагрузка Windows."
            ),
            revert_checked=None,
            final_status="Готово",
        )

    return build_internet_cleanup_error_result("\n".join(failed[:4]))


class InternetCleanupWorker(QThread):
    loaded = pyqtSignal(int, object)
    failed = pyqtSignal(int, str)
    status = pyqtSignal(int, str)

    def __init__(self, request_id: int, *, parent=None):
        super().__init__(parent)
        self._request_id = int(request_id)

    def run(self) -> None:
        try:
            result = run_internet_cleanup(
                status_callback=lambda message: self.status.emit(self._request_id, message),
            )
        except Exception as exc:
            log(f"InternetCleanupWorker: не удалось выполнить сброс сети: {exc}", "WARNING")
            self.failed.emit(self._request_id, str(exc))
            return
        self.loaded.emit(self._request_id, result)


__all__ = [
    "InternetCleanupActionResult",
    "InternetCleanupCommand",
    "InternetCleanupWorker",
    "build_internet_cleanup_commands",
    "build_internet_cleanup_error_result",
    "run_internet_cleanup",
]
