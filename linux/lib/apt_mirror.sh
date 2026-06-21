# Настройка быстрых зеркал apt для России (Kali / Debian / Ubuntu).

setup_apt_mirror_ru() {
    [ -f /etc/os-release ] || {
        log "WARN: /etc/os-release не найден — зеркало не настроено"
        return 0
    }

    # shellcheck disable=SC1091
    . /etc/os-release

    log "Зеркало apt для России (${NAME:-${ID:-linux}})..."

    case "${ID:-}" in
        kali*)
            _apt_mirror_kali_ru
            ;;
        debian*)
            _apt_mirror_debian_ru "${VERSION_CODENAME:-bookworm}"
            ;;
        ubuntu*)
            _apt_mirror_ubuntu_ru "${VERSION_CODENAME:-jammy}"
            ;;
        *)
            log "WARN: ${ID} — автозеркало не поддерживается; используйте --mirror default"
            ;;
    esac
}

_apt_mirror_backup_once() {
    local file="$1"
    [ -f "$file" ] || return 0
    [ -f "${file}.bak.zapret" ] || cp -a "$file" "${file}.bak.zapret"
}

_apt_mirror_sed_kali() {
    local mirror="$1"
    local file="$2"
    [ -f "$file" ] || return 0
    _apt_mirror_backup_once "$file"
    sed -i.zapret \
        -e "s|https\\?://http\\.kali\\.org/kali|${mirror}|g" \
        -e "s|https\\?://kali\\.download/kali|${mirror}|g" \
        "$file" 2>/dev/null || true
}

_apt_mirror_kali_ru() {
    local mirror="https://mirror.truenetwork.ru/kali"
    local suite="kali-rolling"
    local components="main contrib non-free non-free-firmware"

    _apt_mirror_backup_once /etc/apt/sources.list
    _apt_mirror_sed_kali "$mirror" /etc/apt/sources.list

    local f
    for f in /etc/apt/sources.list.d/*.list; do
        [ -f "$f" ] || continue
        _apt_mirror_sed_kali "$mirror" "$f"
    done

    if ! grep -rqE '[[:space:]]kali-rolling[[:space:]]' /etc/apt/sources.list /etc/apt/sources.list.d/ 2>/dev/null; then
        echo "deb ${mirror} ${suite} ${components}" > /etc/apt/sources.list.d/zapret-kali-ru.list
    fi

    log "Kali → ${mirror}"
}

_apt_mirror_debian_ru() {
    local suite="$1"
    local mirror="https://mirror.yandex.ru/debian"
    local components="main contrib non-free non-free-firmware"
    local list="/etc/apt/sources.list.d/zapret-debian-ru.list"

    _apt_mirror_backup_once /etc/apt/sources.list
    if ! grep -qE '[[:space:]]'"${suite}"'[[:space:]]' /etc/apt/sources.list /etc/apt/sources.list.d/*.list 2>/dev/null; then
        echo "deb ${mirror} ${suite} ${components}" > "$list"
    else
        _apt_mirror_backup_once /etc/apt/sources.list
        sed -i.zapret "s|https\\?://deb\\.debian\\.org/debian|${mirror}|g" /etc/apt/sources.list 2>/dev/null || true
        for f in /etc/apt/sources.list.d/*.list; do
            [ -f "$f" ] || continue
            _apt_mirror_backup_once "$f"
            sed -i.zapret "s|https\\?://deb\\.debian\\.org/debian|${mirror}|g" "$f" 2>/dev/null || true
        done
    fi

    log "Debian → ${mirror} (${suite})"
}

_apt_mirror_ubuntu_ru() {
    local suite="$1"
    local mirror="https://mirror.yandex.ru/ubuntu"
    local components="main restricted universe multiverse"
    local list="/etc/apt/sources.list.d/zapret-ubuntu-ru.list"

    _apt_mirror_backup_once /etc/apt/sources.list
    if ! grep -qE '[[:space:]]'"${suite}"'[[:space:]]' /etc/apt/sources.list /etc/apt/sources.list.d/*.list 2>/dev/null; then
        echo "deb ${mirror} ${suite} ${components}" > "$list"
    else
        sed -i.zapret \
            -e "s|https\\?://archive\\.ubuntu\\.com/ubuntu|${mirror}|g" \
            -e "s|https\\?://ru\\.archive\\.ubuntu\\.com/ubuntu|${mirror}|g" \
            /etc/apt/sources.list 2>/dev/null || true
        for f in /etc/apt/sources.list.d/*.list; do
            [ -f "$f" ] || continue
            _apt_mirror_backup_once "$f"
            sed -i.zapret \
                -e "s|https\\?://archive\\.ubuntu\\.com/ubuntu|${mirror}|g" \
                -e "s|https\\?://ru\\.archive\\.ubuntu\\.com/ubuntu|${mirror}|g" \
                "$f" 2>/dev/null || true
        done
    fi

    log "Ubuntu → ${mirror} (${suite})"
}
