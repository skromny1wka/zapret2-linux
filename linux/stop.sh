#!/bin/bash

ZAPRET_LINUX_DIR="$(cd "$(dirname "$0")" && pwd)"
export ZAPRET_LINUX_DIR

# shellcheck source=lib/common.sh
. "${ZAPRET_LINUX_DIR}/lib/common.sh"
load_config
require_linux

if [ "$(id -u)" -ne 0 ]; then
    die "Остановка требует root: sudo $0"
fi

if [ -x "${VENV_DIR}/bin/python" ]; then
    "${VENV_DIR}/bin/python" - <<'PY'
from platform.linux_support import kill_linux_winws_processes
kill_linux_winws_processes()
PY
else
    pkill -x nfqws2 2>/dev/null || true
    nft delete table inet zapret2 2>/dev/null || true
fi

log "Zapret остановлен, nftables очищены."
