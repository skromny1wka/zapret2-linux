# Telegram Proxy refactor

## Goal

Make the Telegram Proxy module easier to maintain without changing its visible UI or network behavior.

## Scope

AC1. `src/telegram_proxy/ui/page.py` must keep page wiring and widget updates, but repeated worker queue state must move to a small helper object.

AC2. Upstream proxy settings must have one canonical builder path. `manager.py` must not keep a second copy of the same settings-read logic.

AC3. `src/telegram_proxy/wss_proxy.py` must be split by responsibility:
- `raw_websocket.py` owns the low-level WebSocket client and handshake error.
- `stats.py` owns proxy statistics.
- `routing.py` owns routing-related configuration and relay probing helpers.
- `relay.py` owns relay constants/helpers that can be moved without changing behavior.

AC4. Existing network behavior must stay the same. The refactor may move code, but must not change Telegram DC routing, WSS fallback, TCP fallback, upstream fallback, or stats semantics.

AC5. Existing Telegram Proxy architecture tests must be updated or extended so the new boundaries are checked.

AC6. Work must stay on `main`; commits must include only files for this task. Unrelated dirty worktree files must not be touched.

## Verification

Run focused Telegram Proxy tests:

```bash
PYTHONPATH=src python -m unittest \
  tests.test_telegram_proxy_actions_architecture \
  tests.test_telegram_proxy_worker_architecture \
  tests.test_telegram_proxy_worker_queue \
  tests.test_telegram_proxy_diagnostics \
  tests.test_telegram_hosts
```

Run architecture checks:

```bash
PYTHONPATH=src python -m app.architecture_checks
```

Run import smoke checks for the split modules:

```bash
PYTHONPATH=src python - <<'PY'
from telegram_proxy.raw_websocket import RawWebSocket, WsHandshakeError
from telegram_proxy.routing import UpstreamProxyConfig, check_relay_reachable
from telegram_proxy.stats import ProxyStats
from telegram_proxy.wss_proxy import TelegramWSProxy
print(RawWebSocket, WsHandshakeError, UpstreamProxyConfig, check_relay_reachable, ProxyStats, TelegramWSProxy)
PY
```
