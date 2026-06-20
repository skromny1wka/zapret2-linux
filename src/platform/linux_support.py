from __future__ import annotations

import os
import re
import subprocess
import sys
from typing import Iterable

QNUM = 200
NFT_TABLE = "zapret2"
DESYNC_MARK = "0x40000000"

_WINDOWS_ONLY_PREFIXES = ("--wf-",)
_WINDOWS_ONLY_EXACT = ("--ctrack-disable=0", "--ctrack-disable=1")

_DEFAULT_TCP_PORTS = "80,443,1080,2053,2083,2087,2096,8443"
_DEFAULT_UDP_PORTS = "80,443,3478,50000-50099"
_PKT_LIMIT = 12

_WF_TCP_OUT_RE = re.compile(r"^--wf-tcp-out=(.+)$", re.IGNORECASE)
_WF_TCP_IN_RE = re.compile(r"^--wf-tcp-in=(.+)$", re.IGNORECASE)
_WF_UDP_OUT_RE = re.compile(r"^--wf-udp-out=(.+)$", re.IGNORECASE)


def is_linux() -> bool:
    return sys.platform == "linux"


def _strip_line(line: str) -> str:
    return str(line or "").strip().rstrip("\r")


def is_windows_only_arg(arg: str) -> bool:
    value = _strip_line(arg)
    if not value:
        return True
    for prefix in _WINDOWS_ONLY_PREFIXES:
        if value.startswith(prefix):
            return True
    return value in _WINDOWS_ONLY_EXACT


def filter_launch_args(args: Iterable[str]) -> list[str]:
    filtered: list[str] = []
    has_qnum = False
    for raw in args:
        arg = _strip_line(raw)
        if not arg or is_windows_only_arg(arg):
            continue
        if arg.startswith("--qnum"):
            has_qnum = True
        filtered.append(arg)
    if not has_qnum:
        filtered.insert(0, f"--qnum={QNUM}")
    return filtered


def adapt_preset_text_for_linux(text: str) -> str:
    lines: list[str] = []
    for raw in str(text or "").splitlines():
        line = _strip_line(raw)
        if not line or line.startswith("#"):
            lines.append(raw.rstrip("\r"))
            continue
        if is_windows_only_arg(line):
            continue
        lines.append(line)
    return "\n".join(lines).strip() + ("\n" if lines else "")


def _extract_ports(text: str, pattern: re.Pattern[str], default: str) -> str:
    found = default
    for raw in str(text or "").splitlines():
        line = _strip_line(raw)
        match = pattern.match(line)
        if match:
            found = match.group(1).strip()
    return found or default


def _merge_udp_ports(base: str) -> str:
    parts: list[str] = []
    seen: set[str] = set()
    for chunk in f"{base},3478,50000-50099".split(","):
        item = chunk.strip()
        if item and item not in seen:
            seen.add(item)
            parts.append(item)
    return ",".join(parts)


def build_nft_script(preset_text: str = "") -> str:
    tcp_out = _extract_ports(preset_text, _WF_TCP_OUT_RE, _DEFAULT_TCP_PORTS)
    tcp_in = _extract_ports(preset_text, _WF_TCP_IN_RE, tcp_out)
    udp_out = _merge_udp_ports(_extract_ports(preset_text, _WF_UDP_OUT_RE, "80,443"))
    udp_in = udp_out

    return f"""
delete table inet {NFT_TABLE}
add table inet {NFT_TABLE}
add chain inet {NFT_TABLE} postnat {{ type filter hook postrouting priority 101; }}
add chain inet {NFT_TABLE} prenat {{ type filter hook prerouting priority -101; }}
add chain inet {NFT_TABLE} predefrag {{ type filter hook output priority -401; }}
add rule inet {NFT_TABLE} predefrag mark and {DESYNC_MARK} != 0 notrack
add rule inet {NFT_TABLE} postnat meta mark and {DESYNC_MARK} == 0 tcp dport {{{tcp_out}}} ct original packets 1-{_PKT_LIMIT} queue num {QNUM} bypass
add rule inet {NFT_TABLE} postnat meta mark and {DESYNC_MARK} == 0 udp dport {{{udp_out}}} ct original packets 1-{_PKT_LIMIT} queue num {QNUM} bypass
add rule inet {NFT_TABLE} prenat meta mark and {DESYNC_MARK} == 0 tcp sport {{{tcp_in}}} ct reply packets 1-{_PKT_LIMIT} queue num {QNUM} bypass
add rule inet {NFT_TABLE} prenat meta mark and {DESYNC_MARK} == 0 udp sport {{{udp_in}}} ct reply packets 1-{_PKT_LIMIT} queue num {QNUM} bypass
""".strip()


def ensure_linux_firewall(preset_text: str = "") -> tuple[bool, str]:
    if not is_linux():
        return True, ""

    try:
        subprocess.run(
            ["sysctl", "-w", "net.netfilter.nf_conntrack_tcp_be_liberal=1"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        result = subprocess.run(
            ["nft", "-f", "-"],
            input=build_nft_script(preset_text),
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return False, "nftables не установлен. Запустите linux/install.sh"

    if result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        return False, err or "Не удалось применить nftables"
    return True, ""


def remove_linux_firewall() -> None:
    if not is_linux():
        return
    try:
        subprocess.run(
            ["nft", "delete", "table", "inet", NFT_TABLE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except FileNotFoundError:
        return


def nftables_table_exists() -> bool:
    if not is_linux():
        return False
    try:
        result = subprocess.run(
            ["nft", "list", "table", "inet", NFT_TABLE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def linux_process_names() -> tuple[str, ...]:
    return ("nfqws2", "winws2.exe", "winws.exe")


def kill_linux_winws_processes() -> int:
    if not is_linux():
        return 0

    try:
        import psutil
    except Exception:
        return 0

    targets = {name.lower() for name in linux_process_names()}
    killed = 0
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            name = str(proc.info.get("name") or "").lower()
            if name not in targets:
                continue
            proc.kill()
            killed += 1
        except Exception:
            continue
    remove_linux_firewall()
    return killed
