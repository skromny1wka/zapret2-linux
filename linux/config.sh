# Zapret Linux installer configuration

ZAPRET_LINUX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ZAPRET_ROOT="$(cd "${ZAPRET_LINUX_DIR}/.." && pwd)"

INSTALL_ROOT="${INSTALL_ROOT:-$ZAPRET_ROOT}"
RUNTIME_SRC="${RUNTIME_SRC:-$(cd "${ZAPRET_ROOT}/../ZapretTwo" 2>/dev/null && pwd)}"
VENV_DIR="${INSTALL_ROOT}/.venv"
NFQWS2="${INSTALL_ROOT}/exe/nfqws2"
LAUNCHER="${INSTALL_ROOT}/linux/zapret-gui"

QNUM=200
NFT_TABLE=zapret2
DESYNC_MARK=0x40000000

ZAPRET2_RELEASE="${ZAPRET2_RELEASE:-v1.0.2}"
ZAPRET2_TARBALL="https://github.com/bol-van/zapret2/releases/download/${ZAPRET2_RELEASE}/zapret2-${ZAPRET2_RELEASE}.tar.gz"
BLOB_REPO="https://github.com/youtubediscord/zapret2-youtube-discord/raw/master/bin"

APT_PACKAGES="nftables ipset curl ca-certificates tar gzip python3 python3-venv python3-pip python3-pyqt6 libnetfilter-queue1 libmnl0 libcap2 libxkbcommon-x11-0 libgl1 libegl1 libdbus-1-3"
APT_PACKAGES_OPTIONAL="build-essential"
APT_PYQT_PACKAGES="python3-pyqt6 python3-pyqt6.qtsvg"

RUNTIME_DIRS="bin lua lists json bat themes ico windivert.filter exe logs tmp"
RUNTIME_FILES="preset-zapret2.txt preset-zapret2-orchestra.txt"
