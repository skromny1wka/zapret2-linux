#!/bin/bash
set -e

ZAPRET_LINUX_DIR="$(cd "$(dirname "$0")" && pwd)"
export ZAPRET_LINUX_DIR

# shellcheck source=lib/common.sh
. "${ZAPRET_LINUX_DIR}/lib/common.sh"
# shellcheck source=lib/runtime_sync.sh
. "${ZAPRET_LINUX_DIR}/lib/runtime_sync.sh"

usage() {
    cat <<EOF
Zapret Linux installer

Usage:
  sudo $0 [options]

Options:
  --prefix PATH          Каталог установки (по умолчанию: корень репозитория)
  --runtime PATH         Каталог с runtime-данными (по умолчанию: ../ZapretTwo)
  --skip-apt             Не вызывать apt (если пакеты уже установлены)
  --skip-apt-update      Не выполнять apt-get update (если зависает на «ожидании заголовков»)
  --skip-blobs           Не скачивать blob-файлы из интернета
  -h, --help             Показать справку

Примеры:
  sudo $0
  sudo $0 --runtime ../ZapretTwo
  sudo $0 --skip-apt-update
  sudo $0 --skip-apt --runtime ../ZapretTwo
EOF
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --prefix)
            INSTALL_ROOT="$2"
            shift 2
            ;;
        --runtime)
            RUNTIME_SRC="$2"
            shift 2
            ;;
        --skip-apt)
            SKIP_APT=1
            shift
            ;;
        --skip-apt-update)
            SKIP_APT_UPDATE=1
            shift
            ;;
        --skip-blobs)
            SKIP_BLOBS=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            die "Неизвестный аргумент: $1"
            ;;
    esac
done

load_config
require_linux
require_root
ensure_dirs

[ -f "${INSTALL_ROOT}/src/main.py" ] || die "Не найден ${INSTALL_ROOT}/src/main.py. Укажите корень репозитория zapret-main через --prefix."
[ -f "${INSTALL_ROOT}/requirements-linux.txt" ] || die "Не найден ${INSTALL_ROOT}/requirements-linux.txt"

log "Установка Zapret для Linux"
log "Каталог: ${INSTALL_ROOT}"
log "Runtime: ${RUNTIME_SRC:-не найден}"

TMP_DIR="$(mktemp -d)"
cleanup() {
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

if command_exists apt-get; then
    install_apt_packages
else
    log "apt-get не найден. Установите вручную: $APT_PACKAGES"
fi

check_install_prerequisites

load_kernel_modules
write_build_stubs
sync_runtime_assets "$RUNTIME_SRC" "$INSTALL_ROOT"
install_nfqws2_binary "$TMP_DIR" "$(uname -m)"
fetch_missing_blobs
setup_python_env
install_launcher
install_desktop_entry

chmod +x "${ZAPRET_LINUX_DIR}/"*.sh 2>/dev/null || true
chmod +x "${ZAPRET_LINUX_DIR}/zapret-gui" 2>/dev/null || true
chmod +x "${ZAPRET_LINUX_DIR}/lib/"*.sh 2>/dev/null || true

log ""
log "Установка завершена."
log "GUI:       sudo ${LAUNCHER}"
log "           или pkexec ${LAUNCHER}"
log "CLI stop:  sudo ${ZAPRET_LINUX_DIR}/stop.sh"
log ""
log "Для обхода DPI нужны права root (NFQUEUE + nftables)."
