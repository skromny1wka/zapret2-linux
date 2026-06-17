from __future__ import annotations

import ntpath
import os
from pathlib import Path

from log.log import log


STARTUP_SHORTCUT_NAME = "ZapretGUI.lnk"
STARTUP_RELATIVE_PATH = (
    "Microsoft",
    "Windows",
    "Start Menu",
    "Programs",
    "Startup",
)


def get_user_startup_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata).joinpath(*STARTUP_RELATIVE_PATH)
    return Path.home().joinpath("AppData", "Roaming", *STARTUP_RELATIVE_PATH)


def get_startup_shortcut_path() -> Path:
    return get_user_startup_dir() / STARTUP_SHORTCUT_NAME


def _dispatch_shell():
    import win32com.client

    return win32com.client.Dispatch("WScript.Shell")


def create_or_update_startup_shortcut(
    exe_path: str,
    *,
    shortcut_path: str | os.PathLike[str] | None = None,
) -> bool:
    """Создаёт ярлык ZapretGUI в автозагрузке текущего пользователя."""
    exe_path = str(exe_path or "").strip()
    if not exe_path:
        log("Startup shortcut create failed: empty exe path", "ERROR")
        return False

    path = Path(shortcut_path) if shortcut_path is not None else get_startup_shortcut_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        shortcut = _dispatch_shell().CreateShortcut(str(path))
        shortcut.TargetPath = exe_path
        shortcut.Arguments = "--tray"
        shortcut.WorkingDirectory = ntpath.dirname(exe_path) or exe_path
        shortcut.IconLocation = exe_path
        shortcut.Save()
        return True
    except Exception as exc:
        log(f"Startup shortcut create failed: {exc}", "WARNING")
        return False


def delete_startup_shortcut(
    *,
    shortcut_path: str | os.PathLike[str] | None = None,
) -> bool:
    path = Path(shortcut_path) if shortcut_path is not None else get_startup_shortcut_path()
    try:
        if not path.exists():
            return False
        path.unlink()
        return True
    except Exception as exc:
        log(f"Startup shortcut delete failed: {exc}", "WARNING")
        return False
