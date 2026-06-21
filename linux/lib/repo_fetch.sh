# Загрузка репозитория без git (curl + tar). GitHub в РФ часто недоступен или висит.

repo_fetch_urls() {
    local owner="${1:-skromny1wka}"
    local name="${2:-zapret2-linux}"
    local branch="${3:-main}"
    printf '%s\n' \
        "https://codeload.github.com/${owner}/${name}/tar.gz/refs/heads/${branch}" \
        "https://github.com/${owner}/${name}/archive/refs/heads/${branch}.tar.gz" \
        "https://ghproxy.net/https://github.com/${owner}/${name}/archive/refs/heads/${branch}.tar.gz" \
        "https://mirror.ghproxy.com/https://github.com/${owner}/${name}/archive/refs/heads/${branch}.tar.gz"
}

repo_fetch_curl() {
    local url="$1"
    local output="$2"
    local label="${3:-archive}"

    curl \
        --fail \
        --location \
        --progress-bar \
        --connect-timeout 20 \
        --max-time 300 \
        --retry 1 \
        --retry-delay 3 \
        --output "$output" \
        "$url"
}

repo_fetch_tarball() {
    local owner="$1"
    local name="$2"
    local branch="$3"
    local output="$4"
    local url

    while IFS= read -r url; do
        [ -n "$url" ] || continue
        log "Скачиваю ${name} (${branch})..."
        log "  ${url}"
        if repo_fetch_curl "$url" "$output" "$name"; then
            echo ""
            return 0
        fi
        echo ""
        log "WARN: зеркало недоступно, пробую следующее..."
        rm -f "$output"
    done < <(repo_fetch_urls "$owner" "$name" "$branch")

    return 1
}

repo_extract_tarball() {
    local tarball="$1"
    local dest="$2"
    local tmp_dir extracted base

    tmp_dir="$(mktemp -d)"
    tar -xzf "$tarball" -C "$tmp_dir" || {
        rm -rf "$tmp_dir"
        return 1
    }

    extracted="$(find "$tmp_dir" -maxdepth 1 -type d ! -path "$tmp_dir" | head -n 1)"
    if [ -z "$extracted" ] || [ ! -f "${extracted}/src/main.py" ]; then
        rm -rf "$tmp_dir"
        return 1
    fi

    base="$(dirname "$dest")"
    mkdir -p "$base"
    rm -rf "$dest"
    mv "$extracted" "$dest"
    rm -rf "$tmp_dir"
    return 0
}

repo_fetch_git_fallback() {
    local url="$1"
    local dest="$2"
    local branch="$3"

    if ! command -v git >/dev/null 2>&1; then
        return 1
    fi

    log "Пробую git (таймаут 90 с)..."
    export GIT_TERMINAL_PROMPT=0
    export GIT_ASKPASS=/bin/false

    if command -v timeout >/dev/null 2>&1; then
        timeout --kill-after=10 90 git clone --depth 1 --branch "$branch" "$url" "$dest"
    else
        git clone --depth 1 --branch "$branch" "$url" "$dest"
    fi
}

install_repo_tree() {
    local dest="$1"
    local owner="${2:-skromny1wka}"
    local name="${3:-zapret2-linux}"
    local branch="${4:-main}"
    local repo_url="${5:-https://github.com/${owner}/${name}.git}"
    local tmp tarball

    if [ -f "${dest}/src/main.py" ]; then
        log "Репозиторий уже есть: ${dest}"
        return 0
    fi

    if ! command -v curl >/dev/null 2>&1; then
        log "ERROR: нужен curl для загрузки архива"
        return 1
    fi

    tmp="$(mktemp -d)"
    tarball="${tmp}/repo.tar.gz"

    if repo_fetch_tarball "$owner" "$name" "$branch" "$tarball"; then
        if repo_extract_tarball "$tarball" "$dest"; then
            rm -rf "$tmp"
            log "Распаковано: ${dest}"
            return 0
        fi
        log "WARN: архив повреждён или неполный"
    fi

    rm -rf "$tmp"
    log "Архив не скачался — пробую git..."
    rm -rf "$dest"
    if repo_fetch_git_fallback "$repo_url" "$dest" "$branch"; then
        [ -f "${dest}/src/main.py" ] && return 0
    fi

    return 1
}
