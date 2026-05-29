from __future__ import annotations


def create_blockcheck_worker(
    *,
    mode: str = "full",
    extra_domains: list[str] | None = None,
    skip_preflight_failed: bool = False,
    parent=None,
):
    from blockcheck.worker import BlockcheckWorker

    return BlockcheckWorker(
        mode=mode,
        extra_domains=extra_domains,
        skip_preflight_failed=skip_preflight_failed,
        parent=parent,
    )


def create_strategy_scan_worker(
    *,
    target: str,
    mode: str = "quick",
    start_index: int = 0,
    scan_protocol: str = "tcp_https",
    udp_games_scope: str = "all",
    runtime_feature,
    parent=None,
):
    from blockcheck.strategy_scan_worker import StrategyScanWorker

    return StrategyScanWorker(
        target=target,
        mode=mode,
        start_index=start_index,
        scan_protocol=scan_protocol,
        udp_games_scope=udp_games_scope,
        runtime_feature=runtime_feature,
        parent=parent,
    )


def load_page_initial_state():
    from blockcheck.page_runtime import load_page_initial_state as _load_page_initial_state

    return _load_page_initial_state()


def prepare_support(*, run_log_file: str | None, mode_label: str, extra_domains: list[str]):
    from blockcheck.page_runtime import prepare_support as _prepare_support

    return _prepare_support(
        run_log_file=run_log_file,
        mode_label=mode_label,
        extra_domains=extra_domains,
    )


def run_user_domain_action(action: str, domain: str):
    import blockcheck.page_runtime as blockcheck_page_runtime

    action_name = str(action or "").strip().lower()
    if action_name == "add":
        return blockcheck_page_runtime.add_user_domain(domain)
    if action_name == "remove":
        blockcheck_page_runtime.remove_user_domain(domain)
        return str(domain or "").strip()
    raise ValueError(f"Неизвестное действие домена BlockCheck: {action_name}")
