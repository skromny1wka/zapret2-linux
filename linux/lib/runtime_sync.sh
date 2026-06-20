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
    if ! curl_fetch "$ZAPRET2_TARBALL" "${tmp_dir}/zapret2.tar.gz" "nfqws2 (${ZAPRET2_RELEASE})"; then
        die "Не удалось скачать zapret2. Проверьте интернет или задайте ZAPRET2_RELEASE/ZAPRET2_TARBALL."
    fi
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
    if [ "${SKIP_BLOBS:-0}" = "1" ]; then
        log "Пропуск скачивания blob-файлов (--skip-blobs)"
        return 0
    fi

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
        if curl_fetch "${BLOB_REPO}/${blob}" "$target" "blob ${blob}"; then
            log "  blob: ${blob}"
        else
            rm -f "$target"
            log "  WARN: blob не скачан: ${blob}"
        fi
    done
}

setup_python_env() {
    local req_file="${INSTALL_ROOT}/requirements-linux.txt"
    local pip_bin=""
    local venv_flags=()

    log "Создаю Python venv..."

    if [ "${USE_APT_PYQT:-1}" = "1" ] && python3 -c "import PyQt6" 2>/dev/null; then
        log "PyQt6 найден в системе — venv с --system-site-packages"
        venv_flags=(--system-site-packages)
        req_file="${INSTALL_ROOT}/requirements-linux-core.txt"
    elif [ "${USE_APT_PYQT:-1}" = "1" ] && [ -f "${INSTALL_ROOT}/requirements-linux-core.txt" ]; then
        log "Буду ставить только лёгкие pip-пакеты (PyQt6 — из apt или --pip-pyqt)"
        req_file="${INSTALL_ROOT}/requirements-linux-core.txt"
    fi

    if [ ! -f "$req_file" ]; then
        req_file="${INSTALL_ROOT}/requirements-linux.txt"
    fi

    if [ "${USE_APT_PYQT:-0}" != "1" ]; then
        log "Режим --pip-pyqt: скачиваю PyQt6 через pip (может долго показывать 0%)"
        req_file="${INSTALL_ROOT}/requirements-linux.txt"
        venv_flags=()
    fi

    python3 -m venv "${venv_flags[@]}" "$VENV_DIR"
    pip_bin="${VENV_DIR}/bin/pip"

    export PIP_DEFAULT_TIMEOUT="${PIP_DEFAULT_TIMEOUT:-60}"
    export PIP_DISABLE_PIP_VERSION_CHECK=1

    log "Обновляю pip..."
    run_with_timeout 120 "$pip_bin" install --upgrade pip

    log "Устанавливаю Python-зависимости из $(basename "$req_file")..."
    log "Если кажется что зависло на 0% — это pip качает пакеты. Ждите или используйте --fast"
    if ! run_with_timeout 900 "$pip_bin" install \
        --retries 3 \
        --timeout 60 \
        --progress-bar off \
        --no-cache-dir \
        -r "$req_file"; then
        die "pip install не завершился за 15 мин. Попробуйте: sudo $0 --fast --runtime ../ZapretTwo"
    fi

    if ! "${VENV_DIR}/bin/python" -c "import PyQt6" 2>/dev/null; then
        die "PyQt6 не найден после установки. На Kali: apt install python3-pyqt6  или  sudo $0 --pip-pyqt"
    fi

    log "Python-окружение готово"
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
