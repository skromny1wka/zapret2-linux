#!/bin/bash
set -e

ZAPRET_LINUX_DIR="$(cd "$(dirname "$0")" && pwd)"
ZAPRET_ROOT="$(cd "${ZAPRET_LINUX_DIR}/.." && pwd)"
VENV_DIR="${ZAPRET_ROOT}/.venv"

if [ ! -x "${VENV_DIR}/bin/python" ]; then
    echo "Python-окружение не найдено. Сначала выполните:"
    echo "  sudo ${ZAPRET_LINUX_DIR}/install.sh"
    exit 1
fi

export PYTHONPATH="${ZAPRET_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"
cd "$ZAPRET_ROOT"

FORCE=0
while [ "$#" -gt 0 ]; do
    case "$1" in
        --force)
            FORCE=1
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--force]"
            echo "Обновляет lists/russia-blacklist.txt и lists/base/ipset-all.txt из реестров РКН/DPI."
            exit 0
            ;;
        *)
            echo "Неизвестный аргумент: $1"
            exit 1
            ;;
    esac
done

export ZAPRET_RKN_SYNC_FORCE="$FORCE"
"${VENV_DIR}/bin/python" -c "
import json, os, sys
from lists.rkn_registry_sync import run_rkn_sync_with_optional_restart
force = os.environ.get('ZAPRET_RKN_SYNC_FORCE', '0') == '1'
result = run_rkn_sync_with_optional_restart(force=force, restart_on_change=False)
print(json.dumps({
    'changed': result.changed,
    'domain_count': result.domain_count,
    'ip_count': result.ip_count,
    'added_domains': result.added_domains,
    'added_ips': result.added_ips,
    'resolved_ips': result.resolved_ips,
    'sources_ok': list(result.sources_ok),
    'sources_failed': list(result.sources_failed),
    'error': result.error,
}, ensure_ascii=False, indent=2))
sys.exit(0 if not result.error else 1)
"
