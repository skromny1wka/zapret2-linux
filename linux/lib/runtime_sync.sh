sync_runtime_assets() {
    local src="$1"
    local dst="$2"

    if [ -z "$src" ] || [ ! -d "$src" ]; then
        log "WARN: runtime-пакет не найден (${src:-не указан}). Пропускаю копирование bin/lua/lists."
        return 0
    fi

    log "Копирую runtime-данные из: $src"

    for dir in bin lua lists json bat themes ico windivert.filter; do
        if [ -d "${src}/${dir}" ]; then
            mkdir -p "${dst}/${dir}"
            cp -a "${src}/${dir}/." "${dst}/${dir}/"
            log "  ${dir}/"
        fi
    done

    for file in preset-zapret2.txt preset-zapret2-orchestra.txt; do
        if [ -f "${src}/${file}" ]; then
            cp -a "${src}/${file}" "${dst}/${file}"
            log "  ${file}"
        fi
    done
}

install_nfqws2_binary() {
    local tmp_dir="$1"
    local arch="$2"
    local zapret_arch=""

    case "$arch" in
        x86_64) zapret_arch="linux-x86_64" ;;
        aarch64|arm64) zapret_arch="linux-arm64" ;;
        i686|i386) zapret_arch="linux-x86" ;;
        armv7l|armv6l) zapret_arch="linux-arm" ;;
        *) die "Неподдерживаемая архитектура: $arch" ;;
    esac

    log "Скачиваю zapret2 ${ZAPRET2_RELEASE}..."
    curl -fsSL "$ZAPRET2_TARBALL" -o "${tmp_dir}/zapret2.tar.gz"
    tar -xzf "${tmp_dir}/zapret2.tar.gz" -C "$tmp_dir"

    local zapret_src
    zapret_src="$(find "$tmp_dir" -maxdepth 1 -type d -name 'zapret2-*' | head -n 1)"
    [ -n "$zapret_src" ] || zapret_src="$(find "$tmp_dir" -maxdepth 1 -mindepth 1 -type d | head -n 1)"

    local nfqws_src="${zapret_src}/binaries/${zapret_arch}/nfqws2"
    [ -f "$nfqws_src" ] || die "nfqws2 не найден для ${zapret_arch}"

    mkdir -p "${INSTALL_ROOT}/exe"
    install -m 755 "$nfqws_src" "$NFQWS2"
    log "Установлен ${NFQWS2}"

    if [ -d "${zapret_src}/files/fake" ]; then
        mkdir -p "${INSTALL_ROOT}/bin"
        cp -n "${zapret_src}/files/fake/"*.bin "${INSTALL_ROOT}/bin/" 2>/dev/null || true
    fi
}

fetch_missing_blobs() {
    local blob target
    local blob_list="
tls_clienthello_1.bin
tls_clienthello_2.bin
tls_clienthello_2n.bin
tls_clienthello_3.bin
tls_clienthello_4.bin
tls_clienthello_5.bin
tls_clienthello_6.bin
tls_clienthello_7.bin
tls_clienthello_8.bin
tls_clienthello_9.bin
tls_clienthello_10.bin
tls_clienthello_11.bin
tls_clienthello_12.bin
tls_clienthello_13.bin
tls_clienthello_14.bin
tls_clienthello_17.bin
tls_clienthello_18.bin
tls_clienthello_www_google_com.bin
tls_clienthello_sberbank_ru.bin
tls_clienthello_vk_com.bin
tls_clienthello_vk_com_kyber.bin
tls_clienthello_chat_deepseek_com.bin
tls_clienthello_max_ru.bin
tls_clienthello_iana_org.bin
tls_clienthello_4pda_to.bin
tls_clienthello_gosuslugi_ru.bin
syn_packet.bin
dtls_clienthello_w3_org.bin
quic_initial_www_google_com.bin
quic_initial_vk_com.bin
quic_1.bin
quic_2.bin
quic_3.bin
quic_4.bin
quic_5.bin
quic_6.bin
quic_7.bin
quic_test_00.bin
fake_tls_1.bin
fake_tls_2.bin
fake_tls_3.bin
fake_tls_4.bin
fake_tls_5.bin
fake_tls_6.bin
fake_tls_7.bin
fake_tls_8.bin
fake_quic.bin
fake_quic_1.bin
fake_quic_2.bin
fake_quic_3.bin
"

    mkdir -p "${INSTALL_ROOT}/bin"
    for blob in $blob_list; do
        target="${INSTALL_ROOT}/bin/${blob}"
        if [ -f "$target" ]; then
            continue
        fi
        if curl -fsSL "${BLOB_REPO}/${blob}" -o "$target"; then
            log "  blob: ${blob}"
        else
            rm -f "$target"
            log "  WARN: blob не скачан: ${blob}"
        fi
    done
}

setup_python_env() {
    log "Создаю Python venv..."
    python3 -m venv "$VENV_DIR"
    "${VENV_DIR}/bin/pip" install --upgrade pip
    "${VENV_DIR}/bin/pip" install -r "${INSTALL_ROOT}/requirements-linux.txt"
}

install_launcher() {
    install -m 755 "${ZAPRET_LINUX_DIR}/zapret-gui" "$LAUNCHER"

    if [ -d /usr/local/bin ]; then
        ln -sf "$LAUNCHER" /usr/local/bin/zapret-gui
        log "Ссылка: /usr/local/bin/zapret-gui"
    fi
}

load_kernel_modules() {
    modprobe nfnetlink 2>/dev/null || true
    modprobe nfnetlink_queue 2>/dev/null || true
}

install_desktop_entry() {
    local apps_dir="/usr/share/applications"
    [ -d "$apps_dir" ] || return 0

    cat > "${apps_dir}/zapret-gui.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Zapret GUI
Comment=Zapret DPI bypass launcher
Exec=pkexec env DISPLAY=${DISPLAY:-:0} XAUTHORITY=${XAUTHORITY:-$HOME/.Xauthority} ${LAUNCHER}
Icon=${INSTALL_ROOT}/ico/Zapret2.ico
Terminal=false
Categories=Network;
EOF
    log "Desktop entry: ${apps_dir}/zapret-gui.desktop"
}
