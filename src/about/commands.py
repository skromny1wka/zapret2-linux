from __future__ import annotations

import os
import subprocess
import webbrowser
from dataclasses import dataclass

from log.log import log


@dataclass(slots=True)
class AboutActionResult:
    ok: bool
    message: str


def open_support_discussions() -> AboutActionResult:
    from config.urls import SUPPORT_DISCUSSIONS_URL

    try:
        webbrowser.open(SUPPORT_DISCUSSIONS_URL)
        log(f"Открыт GitHub Discussions: {SUPPORT_DISCUSSIONS_URL}", "INFO")
        return AboutActionResult(True, SUPPORT_DISCUSSIONS_URL)
    except Exception as e:
        return AboutActionResult(False, str(e))


def open_telegram(domain: str, *, post: int | None = None) -> AboutActionResult:
    try:
        from config.telegram_links import open_telegram_link

        open_telegram_link(domain, post=post)
        log(f"Открыт Telegram: {domain}", "INFO")
        return AboutActionResult(True, domain)
    except Exception as e:
        return AboutActionResult(False, str(e))


def open_discord(url: str) -> AboutActionResult:
    try:
        webbrowser.open(url)
        log(f"Открыт Discord: {url}", "INFO")
        return AboutActionResult(True, url)
    except Exception as e:
        return AboutActionResult(False, str(e))


def open_github(url: str) -> AboutActionResult:
    try:
        webbrowser.open(url)
        log(f"Открыт GitHub: {url}", "INFO")
        return AboutActionResult(True, url)
    except Exception as e:
        return AboutActionResult(False, str(e))


def open_help_folder() -> AboutActionResult:
    from config.config import HELP_FOLDER

    try:
        if os.path.exists(HELP_FOLDER):
            subprocess.Popen(f'explorer "{HELP_FOLDER}"')
            log(f"Открыта папка: {HELP_FOLDER}", "INFO")
            return AboutActionResult(True, HELP_FOLDER)
        return AboutActionResult(False, "Папка с инструкциями не найдена")
    except Exception as e:
        return AboutActionResult(False, str(e))


__all__ = [
    "AboutActionResult",
    "open_discord",
    "open_github",
    "open_help_folder",
    "open_support_discussions",
    "open_telegram",
]
