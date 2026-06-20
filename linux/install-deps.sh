#!/bin/bash
# Отдельная установка системных пакетов через apt.
# Запускайте один раз, если основной install.sh не должен трогать apt.
set -e

ZAPRET_LINUX_DIR="$(cd "$(dirname "$0")" && pwd)"
export ZAPRET_LINUX_DIR
export SKIP_APT=0

# shellcheck source=lib/common.sh
. "${ZAPRET_LINUX_DIR}/lib/common.sh"
load_config
require_linux
require_root

log "Установка системных пакетов Zapret через apt"
log "Если зависает на «Ожидание заголовков» — смените зеркало Kali или прервите Ctrl+C и повторите позже"

read_apt_opts
export DEBIAN_FRONTEND=noninteractive

if [ "${1:-}" = "--with-update" ]; then
    log "apt-get update (таймаут 90 с)..."
    run_with_timeout 90 apt-get "${APT_OPTS[@]}" update || log "WARN: update не удался"
fi

log "apt-get install (таймаут 10 мин)..."
# shellcheck disable=SC2086
run_with_timeout 600 apt-get "${APT_OPTS[@]}" install -y --no-install-recommends $APT_PACKAGES $APT_PYQT_PACKAGES

log "Готово. Теперь:"
log "  sudo ${ZAPRET_LINUX_DIR}/install.sh --runtime ../ZapretTwo"
