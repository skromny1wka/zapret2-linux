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
