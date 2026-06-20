log() {
    printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*"
}

die() {
    log "ERROR: $*"
    exit 1
}

require_root() {
    if [ "$(id -u)" -ne 0 ]; then
        die "Запустите установщик от root: sudo $0"
    fi
}

require_linux() {
    case "$(uname -s)" in
        Linux) ;;
        *) die "Поддерживается только Linux (обнаружено: $(uname -s))" ;;
    esac
}

load_config() {
    # shellcheck source=/dev/null
    . "${ZAPRET_LINUX_DIR}/config.sh"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

curl_fetch() {
    local url="$1"
    local output="$2"
    local label="${3:-download}"

    if ! command_exists curl; then
        die "curl не найден. Установите curl или запустите установку с уже установленными зависимостями."
    fi

    log "Загрузка ${label}..."
    if curl \
        --fail \
        --location \
        --progress-bar \
        --connect-timeout 20 \
        --max-time 300 \
        --retry 2 \
        --retry-delay 2 \
        --output "$output" \
        "$url"; then
        echo ""
        return 0
    fi

    echo ""
    log "WARN: не удалось скачать ${label}: ${url}"
    return 1
}

run_with_timeout() {
    local seconds="$1"
    shift

    if command_exists timeout; then
        timeout --kill-after=15 "$seconds" "$@"
    else
        "$@"
    fi
}

apt_common_opts() {
    printf '%s\n' \
        -o "Dpkg::Options::=--force-confdef" \
        -o "Dpkg::Options::=--force-confold" \
        -o "Acquire::http::Timeout=20" \
        -o "Acquire::https::Timeout=20" \
        -o "Acquire::ftp::Timeout=20" \
        -o "Acquire::Retries=2" \
        -o "Acquire::ForceIPv4=true"
}

read_apt_opts() {
    APT_OPTS=()
    local opt
    while IFS= read -r opt; do
        [ -n "$opt" ] || continue
        APT_OPTS+=("$opt")
    done < <(apt_common_opts)
}

install_apt_packages() {
    local pkg

    if [ "${SKIP_APT:-0}" = "1" ]; then
        log "apt отключён — пакеты не ставятся (нет «ожидания заголовков»)"
        return 0
    fi

    if ! command_exists apt-get; then
        log "apt-get не найден. Установите вручную: $APT_PACKAGES"
        return 0
    fi

    export DEBIAN_FRONTEND=noninteractive
    read_apt_opts

    if [ "${SKIP_APT_UPDATE:-1}" = "1" ]; then
        log "Пропуск apt-get update (по умолчанию; для update: --with-apt-update)"
    else
        log "Обновляю списки пакетов (жёсткий таймаут 90 с)..."
        if ! run_with_timeout 90 apt-get "${APT_OPTS[@]}" update; then
            log "WARN: apt-get update не удался. Продолжаю без update."
        fi
    fi

    log "Устанавливаю системные пакеты (таймаут 10 мин)..."
    # shellcheck disable=SC2086
    if run_with_timeout 600 apt-get "${APT_OPTS[@]}" install -y --no-install-recommends $APT_PACKAGES; then
        log "Основные пакеты установлены"
    else
        log "WARN: пакетный набор не установился целиком. Пробую по одному..."
        for pkg in $APT_PACKAGES; do
            run_with_timeout 180 apt-get "${APT_OPTS[@]}" install -y --no-install-recommends "$pkg" || \
                log "WARN: пакет не установлен: $pkg"
        done
    fi

    if [ "${USE_APT_PYQT:-1}" = "1" ]; then
        log "PyQt6 из apt (быстрее, чем pip)..."
        # shellcheck disable=SC2086
        run_with_timeout 300 apt-get "${APT_OPTS[@]}" install -y --no-install-recommends $APT_PYQT_PACKAGES || \
            log "WARN: python3-pyqt6 из apt не установлен — pip попробует сам"
    fi
}

check_install_prerequisites() {
    local missing=""

    for cmd in python3 curl tar gzip nft; do
        if ! command_exists "$cmd"; then
            missing="${missing} ${cmd}"
        fi
    done

    if [ -n "$missing" ]; then
        log "ERROR: не хватает:${missing}"
        print_manual_deps_hint
        die "Установите зависимости вручную (см. выше) и запустите install.sh снова"
    fi
}

print_manual_deps_hint() {
    cat <<EOF

--- Зависимости (без install.sh, чтобы apt не зависал) ---
  sudo apt install -y python3 python3-venv python3-pip python3-pyqt6 nftables curl ipset

Или только скрипт apt (отдельно):
  sudo linux/install-deps.sh

Потом:
  sudo linux/install.sh --runtime /path/to/ZapretTwo

EOF
}

ensure_dirs() {
    for dir in $RUNTIME_DIRS; do
        mkdir -p "${INSTALL_ROOT}/${dir}"
    done
}

write_build_stubs() {
    local cfg="${INSTALL_ROOT}/src/config"
    mkdir -p "$cfg"
    cat > "${cfg}/build_info.py" <<'EOF'
CHANNEL='stable'
APP_VERSION='linux-dev'
EOF
    cat > "${cfg}/_build_secrets.py" <<'EOF'
TG_UPDATE_BOT_TOKEN=''
GITHUB_UPDATE_TOKEN=''
TG_LOG_BOT_TOKEN_PROD=''
TG_LOG_BOT_TOKEN_DEV=''
TG_LOG_CHAT_ID=0
UPDATE_SERVERS=[]
PREMIUM_API_BASE_URL=''
EOF
}
