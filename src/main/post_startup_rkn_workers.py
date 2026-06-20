from __future__ import annotations

from log.log import log


def run_rkn_registry_sync_worker(*, runtime_feature=None, force: bool = False) -> dict:
    try:
        from lists.rkn_registry_sync import run_rkn_sync_with_optional_restart

        result = run_rkn_sync_with_optional_restart(
            runtime_feature=runtime_feature,
            force=force,
            restart_on_change=True,
        )
        return {
            "changed": bool(result.changed),
            "domain_count": int(result.domain_count),
            "ip_count": int(result.ip_count),
            "added_domains": int(result.added_domains),
            "added_ips": int(result.added_ips),
            "resolved_ips": int(result.resolved_ips),
            "sources_ok": list(result.sources_ok),
            "sources_failed": list(result.sources_failed),
            "error": str(result.error or ""),
        }
    except Exception as exc:
        log(f"RKN sync worker error: {exc}", "ERROR")
        return {"changed": False, "error": str(exc)}
