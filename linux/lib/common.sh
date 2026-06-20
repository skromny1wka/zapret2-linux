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
        --silent \
        --show-error \
        --connect-timeout 20 \
        --max-time 180 \
        --retry 2 \
        --retry-delay 2 \
        --output "$output" \
        "$url"; then
        return 0
    fi

    log "WARN: не удалось скачать ${label}: ${url}"
    return 1
}

apt_common_opts() {
    printf '%s\n' \
        -o "Dpkg::Options::=--force-confdef" \
        -o "Dpkg::Options::=--force-confold" \
        -o "Acquire::http::Timeout=30" \
        -o "Acquire::https::Timeout=30" \
        -o "Acquire::ftp::Timeout=30" \
        -o "Acquire::Retries=3" \
        -o "Acquire::ForceIPv4=true"
}

install_apt_packages() {
    local pkg

    if [ "${SKIP_APT:-0}" = "1" ]; then
        log "Пропуск apt (--skip-apt)"
        return 0
    fi

    if ! command_exists apt-get; then
        log "apt-get не найден. Установите вручную: $APT_PACKAGES"
        return 0
    fi

    export DEBIAN_FRONTEND=noninteractive

    local -a apt_opts=()
    while IFS= read -r opt; do
        [ -n "$opt" ] || continue
        apt_opts+=("$opt")
    done < <(apt_common_opts)

    if [ "${SKIP_APT_UPDATE:-0}" != "1" ]; then
        log "Обновляю списки пакетов (таймаут 30 с на зеркало)..."
        if ! apt-get "${apt_opts[@]}" update; then
            log "WARN: apt-get update завис или завершился с ошибкой."
            log "      Продолжаю без update. Если установка упадёт — повторите с --skip-apt-update или --skip-apt"
        fi
    else
        log "Пропуск apt-get update (--skip-apt-update)"
    fi

    log "Устанавливаю системные пакеты..."
    # shellcheck disable=SC2086
    if apt-get "${apt_opts[@]}" install -y --no-install-recommends $APT_PACKAGES; then
        return 0
    fi

    log "WARN: не все пакеты установлены одним вызовом. Пробую по одному..."
    for pkg in $APT_PACKAGES; do
        apt-get "${apt_opts[@]}" install -y --no-install-recommends "$pkg" || \
            log "WARN: пакет не установлен: $pkg"
    done
}

check_install_prerequisites() {
    local missing=""

    for cmd in python3 curl tar gzip; do
        if ! command_exists "$cmd"; then
            missing="${missing} ${cmd}"
        fi
    done

    if [ -n "$missing" ]; then
        die "Не хватает команд:${missing}. Установите зависимости или уберите --skip-apt."
    fi
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
