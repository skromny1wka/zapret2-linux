from __future__ import annotations

import os
import sys


def is_elevated() -> bool:
    if sys.platform == "win32":
        try:
            import ctypes

            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False


def require_elevated_or_exit(*, program_name: str = "Zapret") -> None:
    if is_elevated():
        return
    message = (
        f"{program_name} на Linux требует права root для NFQUEUE/nftables.\n"
        f"Запустите: sudo linux/zapret-gui"
    )
    print(message, file=sys.stderr)
    raise SystemExit(1)


def show_error(message: str, *, title: str = "Zapret") -> None:
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(None, message, title, 0x10)
            return
        except Exception:
            pass
    print(f"{title}: {message}", file=sys.stderr)


def show_info(message: str, *, title: str = "Zapret") -> None:
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(None, message, title, 0x40)
            return
        except Exception:
            pass
    print(f"{title}: {message}")
