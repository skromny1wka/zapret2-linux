from __future__ import annotations


def run_startup_update_check() -> dict:
    from updater.startup_update_check import check_for_update_sync

    return check_for_update_sync()
