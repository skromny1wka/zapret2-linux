#!/bin/bash
# Полная установка Zapret для Linux: зеркало apt (РФ) + зависимости + nfqws2 + GUI.
set -e

ZAPRET_REPO_URL="${ZAPRET_REPO_URL:-https://github.com/skromny1wka/zapret2-linux.git}"
ZAPRET_REPO_BRANCH="${ZAPRET_REPO_BRANCH:-main}"
ZAPRET_RAW_BASE="${ZAPRET_RAW_BASE:-https://raw.githubusercontent.com/skromny1wka/zapret2-linux/main}"
INSTALL_DIR="${INSTALL_DIR:-}"
RUNTIME_SRC=""
MIRROR_MODE="ru"
SKIP_MIRROR=0
SKIP_APT=0
SKIP_CLONE=0
EXTRA_INSTALL_ARGS=()

log() {
    printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*"
}

usage() {
    cat <<EOF
Zapret — полная установка одной командой

Usage:
  sudo $0 [options]

Options:
  --runtime PATH       Папка ZapretTwo (bin, lua, lists). Если рядом: ../ZapretTwo
  --install-dir PATH   Куда клонировать репозиторий (по умолчанию: рядом со скриптом или ~/zapret2-linux)
  --mirror ru          Российское зеркало apt (Kali/Debian/Ubuntu) — по умолчанию
  --mirror default     Не менять sources.list
  --skip-mirror        То же что --mirror default
  --skip-apt           Не вызывать apt (зависимости уже стоят)
  --skip-clone         Не клонировать git (уже в каталоге репозитория)
  --with-blobs         Скачать blob-файлы в install.sh
  --pip-pyqt           PyQt6 через pip вместо apt
  -h, --help           Справка

Примеры:

  # из клонированного репозитория
  cd zapret2-linux
  sudo linux/install-all.sh --runtime ../ZapretTwo

  # одной командой с GitHub (клон + установка)
  curl -fsSL https://raw.githubusercontent.com/skromny1wka/zapret2-linux/main/linux/install-all.sh -o /tmp/install-all.sh
  chmod +x /tmp/install-all.sh
  sudo /tmp/install-all.sh --runtime /path/to/ZapretTwo

  # или короче
  curl -fsSL https://raw.githubusercontent.com/skromny1wka/zapret2-linux/main/linux/install-all.sh | sudo bash -s -- --runtime /path/to/ZapretTwo
EOF
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --runtime)
            RUNTIME_SRC="$2"
            shift 2
            ;;
        --install-dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --mirror)
            MIRROR_MODE="$2"
            shift 2
            ;;
        --skip-mirror)
            SKIP_MIRROR=1
            shift
            ;;
        --skip-apt)
            SKIP_APT=1
            shift
            ;;
        --skip-clone)
            SKIP_CLONE=1
            shift
            ;;
        --with-blobs)
            EXTRA_INSTALL_ARGS+=(--with-blobs)
            shift
            ;;
        --pip-pyqt)
            EXTRA_INSTALL_ARGS+=(--pip-pyqt)
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Неизвестный аргумент: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

if [ "$(id -u)" -ne 0 ]; then
    echo "Запустите от root: sudo $0" >&2
    exit 1
fi

if [ "$(uname -s)" != "Linux" ]; then
    echo "Только Linux." >&2
    exit 1
fi

_resolve_repo_root() {
    local script_path script_dir candidate

    script_path="${BASH_SOURCE[0]}"
    if command -v readlink >/dev/null 2>&1; then
        script_path="$(readlink -f "$script_path" 2>/dev/null || echo "$script_path")"
    fi
    script_dir="$(cd "$(dirname "$script_path")" && pwd)"

    if [ -f "${script_dir}/../src/main.py" ]; then
        ZAPRET_LINUX_DIR="$script_dir"
        INSTALL_ROOT="$(cd "${script_dir}/.." && pwd)"
        return 0
    fi

    if [ -n "$INSTALL_DIR" ]; then
        INSTALL_ROOT="$(cd "$INSTALL_DIR" 2>/dev/null && pwd || echo "$INSTALL_DIR")"
    else
        INSTALL_ROOT="${HOME}/zapret2-linux"
    fi
    ZAPRET_LINUX_DIR="${INSTALL_ROOT}/linux"
}

_ensure_repo() {
    if [ -f "${INSTALL_ROOT}/src/main.py" ]; then
        log "Репозиторий: ${INSTALL_ROOT}"
        return 0
    fi

    if [ "$SKIP_CLONE" = "1" ]; then
        echo "ERROR: не найден ${INSTALL_ROOT}/src/main.py и --skip-clone" >&2
        exit 1
    fi

    if ! command -v git >/dev/null 2>&1; then
        echo "ERROR: нужен git. Установите: apt install -y git" >&2
        exit 1
    fi

    log "Клонирую ${ZAPRET_REPO_URL} → ${INSTALL_ROOT}"
    mkdir -p "$(dirname "$INSTALL_ROOT")"
    if [ -d "$INSTALL_ROOT/.git" ]; then
        git -C "$INSTALL_ROOT" fetch origin
        git -C "$INSTALL_ROOT" checkout "$ZAPRET_REPO_BRANCH"
        git -C "$INSTALL_ROOT" pull --ff-only origin "$ZAPRET_REPO_BRANCH" || true
    else
        git clone --depth 1 --branch "$ZAPRET_REPO_BRANCH" "$ZAPRET_REPO_URL" "$INSTALL_ROOT"
    fi

    [ -f "${INSTALL_ROOT}/src/main.py" ] || {
        echo "ERROR: клон не удался: ${INSTALL_ROOT}" >&2
        exit 1
    }
}

_ensure_minimal_tools() {
    if command -v curl >/dev/null 2>&1 && command -v git >/dev/null 2>&1; then
        return 0
    fi
    if [ "$SKIP_APT" = "1" ] || ! command -v apt-get >/dev/null 2>&1; then
        [ -x "$(command -v curl)" ] || { echo "ERROR: нужен curl" >&2; exit 1; }
        [ -x "$(command -v git)" ] || { echo "ERROR: нужен git" >&2; exit 1; }
        return 0
    fi
    log "Ставлю curl, git, ca-certificates..."
    export DEBIAN_FRONTEND=noninteractive
    apt-get install -y --no-install-recommends curl ca-certificates git || true
}

_mirror_kali_ru_fallback() {
    [ -f /etc/os-release ] || return 0
    # shellcheck disable=SC1091
    . /etc/os-release
    [ "${ID:-}" = "kali" ] || return 0
    local mirror="https://mirror.truenetwork.ru/kali"
    log "Kali → ${mirror} (fallback)"
    if [ -f /etc/apt/sources.list ] && [ ! -f /etc/apt/sources.list.bak.zapret ]; then
        cp -a /etc/apt/sources.list /etc/apt/sources.list.bak.zapret
    fi
    if [ -f /etc/apt/sources.list ]; then
        sed -i.zapret \
            -e "s|https\\?://http\\.kali\\.org/kali|${mirror}|g" \
            -e "s|https\\?://kali\\.download/kali|${mirror}|g" \
            /etc/apt/sources.list 2>/dev/null || true
    fi
    if ! grep -rqE '[[:space:]]kali-rolling[[:space:]]' /etc/apt/sources.list /etc/apt/sources.list.d/ 2>/dev/null; then
        echo "deb ${mirror} kali-rolling main contrib non-free non-free-firmware" \
            > /etc/apt/sources.list.d/zapret-kali-ru.list
    fi
}

_load_apt_mirror_lib() {
    local local_lib="${ZAPRET_LINUX_DIR}/lib/apt_mirror.sh"
    if [ -f "$local_lib" ]; then
        # shellcheck source=lib/apt_mirror.sh
        . "$local_lib"
        return 0
    fi
    if ! command -v curl >/dev/null 2>&1; then
        return 1
    fi
    local tmp
    tmp="$(mktemp)"
    if curl -fsSL "${ZAPRET_RAW_BASE}/linux/lib/apt_mirror.sh" -o "$tmp"; then
        # shellcheck source=/dev/null
        . "$tmp"
        rm -f "$tmp"
        return 0
    fi
    rm -f "$tmp"
    return 1
}

_setup_apt_ru_mirror() {
    if [ "$SKIP_MIRROR" = "1" ] || [ "$MIRROR_MODE" != "ru" ]; then
        return 0
    fi
    if _load_apt_mirror_lib; then
        setup_apt_mirror_ru
    else
        _mirror_kali_ru_fallback
    fi
}

_run_apt_update() {
    export DEBIAN_FRONTEND=noninteractive
    local opts=(-o "Dpkg::Options::=--force-confdef" -o "Dpkg::Options::=--force-confold"
        -o "Acquire::http::Timeout=20" -o "Acquire::https::Timeout=20"
        -o "Acquire::Retries=2" -o "Acquire::ForceIPv4=true")
    log "apt-get update (таймаут 120 с)..."
    if command -v timeout >/dev/null 2>&1; then
        timeout --kill-after=15 120 apt-get "${opts[@]}" update || log "WARN: apt update не удался"
    else
        apt-get "${opts[@]}" update || log "WARN: apt update не удался"
    fi
}

_resolve_repo_root
INSTALL_ROOT="${INSTALL_ROOT:-${HOME}/zapret2-linux}"
ZAPRET_LINUX_DIR="${ZAPRET_LINUX_DIR:-${INSTALL_ROOT}/linux}"

log "========== Zapret: полная установка =========="

_resolve_repo_root

if [ "$SKIP_APT" != "1" ] && command -v apt-get >/dev/null 2>&1; then
    _mirror_kali_ru_fallback
    _setup_apt_ru_mirror
    _run_apt_update
fi

_ensure_minimal_tools
_ensure_repo

export ZAPRET_LINUX_DIR
# shellcheck source=lib/common.sh
. "${ZAPRET_LINUX_DIR}/lib/common.sh"
load_config

if [ -z "$RUNTIME_SRC" ]; then
    if [ -d "${INSTALL_ROOT}/../ZapretTwo" ]; then
        RUNTIME_SRC="$(cd "${INSTALL_ROOT}/../ZapretTwo" && pwd)"
    elif [ -d "${HOME}/ZapretTwo" ]; then
        RUNTIME_SRC="${HOME}/ZapretTwo"
    fi
fi

if [ -n "$RUNTIME_SRC" ] && [ ! -d "$RUNTIME_SRC" ]; then
    die "Runtime не найден: ${RUNTIME_SRC}"
fi

if [ -z "$RUNTIME_SRC" ]; then
    log "WARN: ZapretTwo не указан — пресеты/lists не скопируются"
    log "       Укажите: --runtime /path/to/ZapretTwo"
fi

chmod +x "${ZAPRET_LINUX_DIR}/install-deps.sh" 2>/dev/null || true
chmod +x "${ZAPRET_LINUX_DIR}/install.sh" 2>/dev/null || true

if [ "$SKIP_APT" != "1" ]; then
    log "========== Зависимости (apt) =========="
    SKIP_APT=0 bash "${ZAPRET_LINUX_DIR}/install-deps.sh"
else
    log "apt пропущен (--skip-apt)"
fi

log "========== Zapret (nfqws2, venv, GUI) =========="
INSTALL_ARGS=(--skip-apt)
if [ -n "$RUNTIME_SRC" ]; then
    INSTALL_ARGS+=(--runtime "$RUNTIME_SRC")
fi
INSTALL_ARGS+=("${EXTRA_INSTALL_ARGS[@]}")

bash "${ZAPRET_LINUX_DIR}/install.sh" "${INSTALL_ARGS[@]}"

log ""
log "Готово."
log "Запуск GUI:  sudo ${INSTALL_ROOT}/linux/zapret-gui"
log "Остановка:   sudo ${INSTALL_ROOT}/linux/stop.sh"
if [ -z "$RUNTIME_SRC" ]; then
    log ""
    log "Подсказка: скопируйте runtime и переустановите:"
    log "  sudo ${ZAPRET_LINUX_DIR}/install.sh --runtime /path/to/ZapretTwo"
fi
