# dns/dns_core.py
"""
Базовые утилиты и DNSManager на Win32 API.
Быстрая работа без PowerShell/netsh.
"""
from __future__ import annotations

import ctypes, ipaddress, socket, struct, platform, sys, uuid
try:
    import winreg
except ImportError:  # pragma: no cover - модуль есть только на Windows
    winreg = None
from ctypes import wintypes, POINTER, Structure, c_ulong, c_wchar_p
from functools import lru_cache
from typing import List, Tuple, Dict, Optional
from log.log import log


# ──────────────────────────────────────────────────────────────────────
#  Win32 API структуры и константы
# ──────────────────────────────────────────────────────────────────────

# IP Helper API
iphlpapi = getattr(getattr(ctypes, "windll", None), "iphlpapi", None)

# Константы
MAX_ADAPTER_NAME_LENGTH = 256
MAX_ADAPTER_DESCRIPTION_LENGTH = 128
MAX_ADAPTER_ADDRESS_LENGTH = 8
ERROR_SUCCESS = 0
ERROR_BUFFER_OVERFLOW = 111
MIB_IF_TYPE_ETHERNET = 6
MIB_IF_TYPE_PPP = 23
MIB_IF_TYPE_LOOPBACK = 24
DNS_INTERFACE_SETTINGS_VERSION1 = 1
DNS_SETTING_IPV6 = 0x0001
DNS_SETTING_NAMESERVER = 0x0002


class GUID(Structure):
    _fields_ = [
        ("Data1", ctypes.c_uint32),
        ("Data2", ctypes.c_uint16),
        ("Data3", ctypes.c_uint16),
        ("Data4", ctypes.c_ubyte * 8),
    ]


class NET_LUID(Structure):
    _fields_ = [("Value", ctypes.c_uint64)]


class DNS_INTERFACE_SETTINGS(Structure):
    _fields_ = [
        ("Version", ctypes.c_uint32),
        ("Flags", ctypes.c_uint64),
        ("Domain", c_wchar_p),
        ("NameServer", c_wchar_p),
        ("SearchList", c_wchar_p),
        ("RegistrationEnabled", ctypes.c_uint32),
        ("RegisterAdapterName", ctypes.c_uint32),
        ("EnableLLMNR", ctypes.c_uint32),
        ("QueryAdapterName", ctypes.c_uint32),
        ("ProfileNameServer", c_wchar_p),
    ]

class IP_ADDR_STRING(Structure):
    pass

IP_ADDR_STRING._fields_ = [
    ('Next', POINTER(IP_ADDR_STRING)),
    ('IpAddress', c_wchar_p * 16),
    ('IpMask', c_wchar_p * 16),
    ('Context', wintypes.DWORD),
]

class IP_ADAPTER_INFO(Structure):
    pass

IP_ADAPTER_INFO._fields_ = [
    ('Next', POINTER(IP_ADAPTER_INFO)),
    ('ComboIndex', wintypes.DWORD),
    ('AdapterName', ctypes.c_char * (MAX_ADAPTER_NAME_LENGTH + 4)),
    ('Description', ctypes.c_char * (MAX_ADAPTER_DESCRIPTION_LENGTH + 4)),
    ('AddressLength', wintypes.UINT),
    ('Address', ctypes.c_byte * MAX_ADAPTER_ADDRESS_LENGTH),
    ('Index', wintypes.DWORD),
    ('Type', wintypes.UINT),
    ('DhcpEnabled', wintypes.UINT),
    ('CurrentIpAddress', POINTER(IP_ADDR_STRING)),
    ('IpAddressList', IP_ADDR_STRING),
    ('GatewayList', IP_ADDR_STRING),
    ('DhcpServer', IP_ADDR_STRING),
    ('HaveWins', wintypes.BOOL),
    ('PrimaryWinsServer', IP_ADDR_STRING),
    ('SecondaryWinsServer', IP_ADDR_STRING),
    ('LeaseObtained', ctypes.c_int64),
    ('LeaseExpires', ctypes.c_int64),
]

# ──────────────────────────────────────────────────────────────────────
#  Константы исключений
# ──────────────────────────────────────────────────────────────────────
DEFAULT_EXCLUSIONS: list[str] = [
    "vmware", "outline-tap", "openvpn", "virtualbox", "hyper-v", "vmnet",
    "tap-windows", "tuntap", "wireguard", "protonvpn", "proton vpn",
    "radmin vpn", "hamachi", "nordvpn", "expressvpn", "surfshark",
    "pritunl", "zerotier", "tailscale", "loopback", "teredo", "isatap",
    "6to4", "bluetooth", "docker", "wsl", "vethernet"
]

# ──────────────────────────────────────────────────────────────────────
#  Вспомогательные функции
# ──────────────────────────────────────────────────────────────────────

def _normalize_alias(alias: str) -> str:
    """Нормализация имени адаптера"""
    if not isinstance(alias, str):
        return alias
    repl = (
        ('\u00A0', ' '),
        ('\u200E', ''),
        ('\u200F', ''),
        ('\t', ' '),
    )
    for bad, good in repl:
        alias = alias.replace(bad, good)
    return alias.strip()

@lru_cache(maxsize=1)
def _get_dynamic_exclusions() -> list[str]:
    """Возвращает список исключений"""
    return [x.lower() for x in DEFAULT_EXCLUSIONS]

def refresh_exclusion_cache() -> None:
    """Сброс кэша исключений"""
    _get_dynamic_exclusions.cache_clear()

# ──────────────────────────────────────────────────────────────────────
#  Низкоуровневые Win32 функции
# ──────────────────────────────────────────────────────────────────────

def get_adapters_info_native() -> List[Dict]:
    """Получает информацию об адаптерах через IP Helper API"""
    adapters = []
    if iphlpapi is None:
        log("IP Helper API недоступен", "DEBUG")
        return adapters
    
    # Получаем размер буфера
    size = c_ulong(0)
    result = iphlpapi.GetAdaptersInfo(None, ctypes.byref(size))
    
    if result != ERROR_BUFFER_OVERFLOW:
        if result != ERROR_SUCCESS:
            log(f"GetAdaptersInfo failed: {result}", "ERROR")
            return []
    
    # Выделяем буфер
    buffer = ctypes.create_string_buffer(size.value)
    adapter_info = ctypes.cast(buffer, POINTER(IP_ADAPTER_INFO))
    
    # Получаем данные
    result = iphlpapi.GetAdaptersInfo(adapter_info, ctypes.byref(size))
    
    if result != ERROR_SUCCESS:
        log(f"GetAdaptersInfo failed: {result}", "ERROR")
        return []
    
    # Парсим адаптеры
    current = adapter_info
    while current:
        adapter = current.contents
        
        try:
            name = adapter.Description.decode('cp866', errors='ignore')
            adapter_name = adapter.AdapterName.decode('ascii', errors='ignore')
            
            # Пропускаем loopback
            if adapter.Type == MIB_IF_TYPE_LOOPBACK:
                current = adapter.Next
                continue
            
            adapter_dict = {
                'name': name,
                'adapter_name': adapter_name,
                'index': adapter.Index,
                'type': adapter.Type,
                'dhcp_enabled': bool(adapter.DhcpEnabled),
            }
            
            adapters.append(adapter_dict)
            
        except Exception as e:
            log(f"Error parsing adapter: {e}", "DEBUG")
        
        current = adapter.Next
    
    return adapters

def _guid_from_string(guid: str) -> GUID:
    value = uuid.UUID(str(guid).strip("{}"))
    data4 = (ctypes.c_ubyte * 8)(
        value.clock_seq_hi_variant,
        value.clock_seq_low,
        *value.node.to_bytes(6, "big"),
    )
    return GUID(value.time_low, value.time_mid, value.time_hi_version, data4)


def _guid_to_string(guid: GUID) -> str:
    data4 = bytes(guid.Data4)
    return (
        f"{{{guid.Data1:08X}-{guid.Data2:04X}-{guid.Data3:04X}-"
        f"{data4[0]:02X}{data4[1]:02X}-"
        f"{''.join(f'{item:02X}' for item in data4[2:])}}}"
    )


def _normalize_dns_servers(dns_servers: List[str]) -> list[str]:
    normalized_servers: list[str] = []
    for raw_dns in dns_servers:
        dns = (raw_dns or "").strip()
        if not dns:
            continue
        if dns in normalized_servers:
            continue
        normalized_servers.append(dns)
    return normalized_servers


def _split_dns_server_string(dns_string: str) -> list[str]:
    return [
        ip.strip()
        for ip in str(dns_string or "").replace(";", ",").replace(" ", ",").split(",")
        if ip.strip()
    ]


def _filter_dns_servers_by_family(dns_servers: list[str], is_ipv6: bool) -> list[str]:
    filtered: list[str] = []
    for dns in dns_servers:
        try:
            address = ipaddress.ip_address(dns)
        except ValueError:
            continue
        if address.version == (6 if is_ipv6 else 4):
            filtered.append(dns)
    return filtered


def get_interface_guid_from_alias_winapi(adapter_name: str) -> Optional[str]:
    """Получает GUID интерфейса по имени через IP Helper API."""
    try:
        if iphlpapi is None:
            return None
        alias_to_luid = getattr(iphlpapi, "ConvertInterfaceAliasToLuid", None)
        luid_to_guid = getattr(iphlpapi, "ConvertInterfaceLuidToGuid", None)
        if alias_to_luid is None or luid_to_guid is None:
            return None

        luid = NET_LUID()
        alias_result = alias_to_luid(c_wchar_p(_normalize_alias(adapter_name)), ctypes.byref(luid))
        if alias_result != ERROR_SUCCESS:
            return None

        guid = GUID()
        guid_result = luid_to_guid(ctypes.byref(luid), ctypes.byref(guid))
        if guid_result != ERROR_SUCCESS:
            return None

        return _guid_to_string(guid)
    except Exception as e:
        log(f"Error getting GUID via WinAPI for {adapter_name}: {e}", "DEBUG")
        return None


def get_interface_guid_from_name(adapter_name: str) -> Optional[str]:
    """Получает GUID интерфейса по имени через реестр"""
    guid = get_interface_guid_from_alias_winapi(adapter_name)
    if guid:
        return guid

    try:
        if winreg is None:
            return None
        # Ищем в реестре
        reg_path = r"SYSTEM\CurrentControlSet\Control\Network\{4D36E972-E325-11CE-BFC1-08002BE10318}"
        
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as network_key:
            i = 0
            while True:
                try:
                    guid = winreg.EnumKey(network_key, i)
                    
                    # Пропускаем специальные ключи
                    if not guid.startswith('{'):
                        i += 1
                        continue
                    
                    try:
                        conn_path = f"{reg_path}\\{guid}\\Connection"
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, conn_path) as conn_key:
                            name, _ = winreg.QueryValueEx(conn_key, "Name")
                            
                            if _normalize_alias(name) == _normalize_alias(adapter_name):
                                return guid
                    except:
                        pass
                    
                    i += 1
                except OSError:
                    break
        
    except Exception as e:
        log(f"Error getting GUID for {adapter_name}: {e}", "DEBUG")
    
    return None


def set_dns_via_windows_api(guid: str, dns_servers: List[str], is_ipv6: bool = False) -> bool:
    """Устанавливает DNS через IP Helper API Windows."""
    try:
        if iphlpapi is None:
            log("IP Helper API недоступен для установки DNS", "ERROR")
            return False
        set_interface_dns_settings = getattr(iphlpapi, "SetInterfaceDnsSettings", None)
        if set_interface_dns_settings is None:
            log("SetInterfaceDnsSettings недоступен в IP Helper API", "ERROR")
            return False

        dns_string = ",".join(_normalize_dns_servers(dns_servers))
        settings = DNS_INTERFACE_SETTINGS()
        settings.Version = DNS_INTERFACE_SETTINGS_VERSION1
        settings.Flags = DNS_SETTING_NAMESERVER | (DNS_SETTING_IPV6 if is_ipv6 else 0)
        settings.NameServer = dns_string

        result = set_interface_dns_settings(_guid_from_string(guid), ctypes.byref(settings))
        if result == ERROR_SUCCESS:
            return True

        log(f"SetInterfaceDnsSettings failed: {result}", "ERROR")
        return False
    except Exception as e:
        log(f"Error setting DNS via WinAPI: {e}", "ERROR")
        return False


def get_dns_via_windows_api(guid: str, is_ipv6: bool = False) -> Optional[list[str]]:
    """Читает статические DNS интерфейса через IP Helper API Windows."""
    try:
        if iphlpapi is None:
            return None
        get_interface_dns_settings = getattr(iphlpapi, "GetInterfaceDnsSettings", None)
        if get_interface_dns_settings is None:
            return None

        settings = DNS_INTERFACE_SETTINGS()
        settings.Version = DNS_INTERFACE_SETTINGS_VERSION1
        settings.Flags = 0

        result = get_interface_dns_settings(_guid_from_string(guid), ctypes.byref(settings))
        if result != ERROR_SUCCESS:
            log(f"GetInterfaceDnsSettings failed: {result}", "DEBUG")
            return None

        try:
            raw_dns = settings.NameServer or settings.ProfileNameServer or ""
            return _filter_dns_servers_by_family(
                _split_dns_server_string(raw_dns),
                is_ipv6,
            )
        finally:
            free_interface_dns_settings = getattr(iphlpapi, "FreeInterfaceDnsSettings", None)
            if free_interface_dns_settings is not None:
                free_interface_dns_settings(ctypes.byref(settings))
    except Exception as e:
        log(f"Error getting DNS via WinAPI: {e}", "DEBUG")
        return None

def notify_dns_change():
    """Уведомляет систему об изменении DNS через Win32 API"""
    try:
        # Используем SendNotifyMessage для уведомления оболочки
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x001A
        
        user32 = ctypes.windll.user32
        user32.SendNotifyMessageW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "Environment"
        )
        
        return True
    except Exception as e:
        log(f"Error notifying DNS change: {e}", "DEBUG")
        return False

def flush_dns_cache_native() -> bool:
    """Очищает DNS кэш через Win32 API"""
    try:
        dnsapi = ctypes.windll.dnsapi
        result = dnsapi.DnsFlushResolverCache()
        return True
    except Exception as e:
        log(f"Error flushing DNS cache: {e}", "DEBUG")
        return False

# DoH Template URLs
DOH_TEMPLATES = {
    "1.1.1.1": "https://cloudflare-dns.com/dns-query",
    "1.0.0.1": "https://cloudflare-dns.com/dns-query",
    "8.8.8.8": "https://dns.google/dns-query",
    "8.8.4.4": "https://dns.google/dns-query",
    "9.9.9.9": "https://dns.quad9.net/dns-query",
    "149.112.112.112": "https://dns.quad9.net/dns-query",
    "94.140.14.14": "https://dns.adguard.com/dns-query",
    "94.140.15.15": "https://dns.adguard.com/dns-query",
    "185.222.222.222": "https://doh.sb/dns-query",
    "45.11.45.11": "https://doh.sb/dns-query",
    "208.67.222.222": "https://doh.opendns.com/dns-query",
    "208.67.220.220": "https://doh.opendns.com/dns-query",
    "84.21.189.133": "https://dns.malw.link/dns-query",
    "64.188.98.242": "https://dns.malw.link/dns-query",
    "194.180.189.33": "https://dnsdoh.art:444/dns-query",
    # Xbox DNS (xbox-dns.ru)
    "176.99.11.77": "https://xbox-dns.ru/dns-query",
    "80.78.247.254": "https://xbox-dns.ru/dns-query",
    # Comss DNS (dns.comss.one)
    "83.220.169.155": "https://dns.comss.one/dns-query",
    "212.109.195.93": "https://dns.comss.one/dns-query",
}

# DoH настройки
DOH_AUTO = 0  # Автоматический выбор
DOH_DISABLED = 1  # Отключен
DOH_ENABLED_AUTO_FALLBACK = 2  # Включен с fallback на обычный DNS
DOH_ENABLED_ONLY = 3  # Только DoH, без fallback

# Добавим функции проверки DoH:

def get_windows_version() -> Tuple[int, int, int]:
    """Получает версию Windows"""
    try:
        version = sys.getwindowsversion()
        return (version.major, version.minor, version.build)
    except:
        return (0, 0, 0)

def is_doh_supported() -> bool:
    """Проверяет, поддерживает ли система DoH"""
    try:
        major, minor, build = get_windows_version()
        
        # Windows 11 (build 22000+) или Windows 10 build 19628+
        if major == 10:
            if build >= 22000:  # Windows 11
                return True
            elif build >= 19628:  # Windows 10 Insider Preview с DoH
                return True
        
        return False
    except:
        return False

def get_doh_template_for_dns(dns_ip: str) -> Optional[str]:
    """Возвращает DoH template URL для DNS IP"""
    return DOH_TEMPLATES.get(dns_ip)

def get_doh_settings_for_adapter(guid: str) -> Dict[str, any]:
    """Получает настройки DoH для адаптера"""
    try:
        # Путь к настройкам DoH в реестре
        reg_path = f"SYSTEM\\CurrentControlSet\\Services\\Dnscache\\InterfaceSpecificParameters\\{guid}\\DohInterfaceSettings\\Doh"
        
        result = {
            'supported': is_doh_supported(),
            'enabled': False,
            'template': None,
            'auto_upgrade': False
        }
        
        if not result['supported']:
            return result
        
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0,
                               winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                
                # Проверяем DohFlags (0=авто, 1=выкл, 2=вкл с fallback, 3=только DoH)
                try:
                    flags, _ = winreg.QueryValueEx(key, "DohFlags")
                    result['enabled'] = (flags in [DOH_ENABLED_AUTO_FALLBACK, DOH_ENABLED_ONLY])
                except:
                    pass
                
                # Получаем template
                try:
                    template, _ = winreg.QueryValueEx(key, "DohTemplate")
                    result['template'] = template
                except:
                    pass
                
                # Auto upgrade (автоматическое обновление до DoH)
                try:
                    auto, _ = winreg.QueryValueEx(key, "DohAutoUpgrade")
                    result['auto_upgrade'] = bool(auto)
                except:
                    pass
                    
        except FileNotFoundError:
            # Настройки DoH не заданы для этого адаптера
            pass
        
        return result
        
    except Exception as e:
        log(f"Error getting DoH settings: {e}", "DEBUG")
        return {
            'supported': False,
            'enabled': False,
            'template': None,
            'auto_upgrade': False
        }

def set_doh_for_adapter(guid: str, dns_ip: str, enable: bool = True, 
                        auto_upgrade: bool = True) -> bool:
    """Устанавливает DoH для адаптера"""
    try:
        if not is_doh_supported():
            log("DoH not supported on this Windows version", "WARNING")
            return False
        
        # Получаем DoH template для DNS
        template = get_doh_template_for_dns(dns_ip)
        if not template and enable:
            log(f"No DoH template for {dns_ip}", "WARNING")
            return False
        
        # Путь к настройкам DoH
        reg_path = f"SYSTEM\\CurrentControlSet\\Services\\Dnscache\\InterfaceSpecificParameters\\{guid}\\DohInterfaceSettings\\Doh"
        
        try:
            # Создаем/открываем ключ
            with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, reg_path, 0,
                                   winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
                
                if enable:
                    # Включаем DoH
                    # DohFlags: 2 = включен с fallback на обычный DNS
                    winreg.SetValueEx(key, "DohFlags", 0, winreg.REG_DWORD, 
                                     DOH_ENABLED_AUTO_FALLBACK)
                    
                    # Устанавливаем template
                    winreg.SetValueEx(key, "DohTemplate", 0, winreg.REG_SZ, template)
                    
                    # Auto upgrade
                    if auto_upgrade:
                        winreg.SetValueEx(key, "DohAutoUpgrade", 0, winreg.REG_DWORD, 1)
                    
                    log(f"DoH enabled for GUID {guid}: {template}", "DNS")
                else:
                    # Отключаем DoH
                    winreg.SetValueEx(key, "DohFlags", 0, winreg.REG_DWORD, DOH_DISABLED)
                    log(f"DoH disabled for GUID {guid}", "DNS")
                
                # Уведомляем систему
                notify_dns_change()
                flush_dns_cache_native()
                
                return True
                
        except Exception as e:
            log(f"Error setting DoH registry values: {e}", "ERROR")
            return False
            
    except Exception as e:
        log(f"Error in set_doh_for_adapter: {e}", "ERROR")
        return False

def clear_doh_for_adapter(guid: str) -> bool:
    """Очищает настройки DoH для адаптера"""
    try:
        reg_path = f"SYSTEM\\CurrentControlSet\\Services\\Dnscache\\InterfaceSpecificParameters\\{guid}\\DohInterfaceSettings"
        
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0,
                               winreg.KEY_ALL_ACCESS | winreg.KEY_WOW64_64KEY) as key:
                try:
                    winreg.DeleteKey(key, "Doh")
                    log(f"DoH settings cleared for GUID {guid}", "DNS")
                    notify_dns_change()
                    flush_dns_cache_native()
                    return True
                except:
                    pass
        except:
            pass
        
        return False
        
    except Exception as e:
        log(f"Error clearing DoH: {e}", "DEBUG")
        return False

class DNSManager:
    """Менеджер DNS на основе Win32 API"""
    
    def __init__(self):
        self._wmi_conn = None
        self._adapter_cache = {}
        self._guid_cache = {}
    
    @property
    def wmi_conn(self):
        """Ленивая инициализация WMI"""
        if self._wmi_conn is None:
            try:
                import wmi
                self._wmi_conn = wmi.WMI()
            except:
                self._wmi_conn = False
        return self._wmi_conn if self._wmi_conn else None
    
    @staticmethod
    def should_ignore_adapter(name: str, description: str) -> bool:
        """Проверяет, нужно ли игнорировать адаптер"""
        name = _normalize_alias(name)
        description = _normalize_alias(description)
        
        for pattern in _get_dynamic_exclusions():
            if pattern in name.lower() or pattern in description.lower():
                return True
        return False
    
    def get_network_adapters_fast(
        self,
        include_ignored: bool = False,
        include_disconnected: bool = True
    ) -> List[Tuple[str, str]]:
        """Быстрое получение списка адаптеров через WMI"""
        adapters = []
        
        # Пробуем WMI
        if self.wmi_conn:
            try:
                for adapter in self.wmi_conn.Win32_NetworkAdapter(PhysicalAdapter=True):
                    if not adapter.NetConnectionID or not adapter.Description:
                        continue
                    
                    # Проверяем статус подключения
                    if not include_disconnected and adapter.NetConnectionStatus != 2:
                        continue
                    
                    alias = _normalize_alias(adapter.NetConnectionID)
                    desc = adapter.Description
                    
                    # Проверяем исключения
                    if not include_ignored and self.should_ignore_adapter(alias, desc):
                        continue
                    
                    adapters.append((adapter.NetConnectionID, desc))
                    
                return adapters
                
            except Exception as e:
                log(f"WMI error: {e}", "DEBUG")
        
        # Fallback на нативный API
        try:
            native_adapters = get_adapters_info_native()
            
            for adapter in native_adapters:
                name = adapter['name']
                
                if not include_ignored and self.should_ignore_adapter(name, name):
                    continue
                
                adapters.append((name, name))
                
        except Exception as e:
            log(f"Native API error: {e}", "ERROR")
        
        return adapters
    
    def get_adapter_guid(self, adapter_name: str) -> Optional[str]:
        """Получает GUID адаптера с кешированием"""
        norm_name = _normalize_alias(adapter_name)
        
        if norm_name in self._guid_cache:
            return self._guid_cache[norm_name]
        
        guid = get_interface_guid_from_name(adapter_name)
        
        if guid:
            self._guid_cache[norm_name] = guid
        
        return guid
    
    def get_current_dns(self, adapter_name: str, address_family: str = "IPv4") -> List[str]:
        """Получает текущие статические DNS серверы через Windows API"""
        try:
            guid = self.get_adapter_guid(adapter_name)
            if not guid:
                log(f"GUID not found for {adapter_name}", "DEBUG")
                return []
            
            is_ipv6 = (address_family.lower() == "ipv6")
            dns_list = get_dns_via_windows_api(guid, is_ipv6)
            return dns_list if dns_list is not None else []
            
        except Exception as e:
            log(f"Error getting DNS for {adapter_name}: {e}", "DEBUG")
            return []
    
    def get_all_dns_info_fast(self, adapter_names: List[str]) -> Dict[str, Dict[str, List[str]]]:
        """Быстрое получение DNS для нескольких адаптеров"""
        result = {}
        
        for name in adapter_names:
            norm_name = _normalize_alias(name)
            result[norm_name] = {
                "ipv4": self.get_current_dns(name, "IPv4"),
                "ipv6": self.get_current_dns(name, "IPv6")
            }
        
        return result
    
    def set_custom_dns(
        self,
        adapter_name: str,
        primary_dns: str,
        secondary_dns: Optional[str] = None,
        address_family: str = "IPv4"
    ) -> Tuple[bool, str]:
        """Устанавливает пользовательские DNS через Windows API"""
        try:
            guid = self.get_adapter_guid(adapter_name)
            if not guid:
                return False, "GUID not found"
            
            dns_list = [primary_dns]
            if secondary_dns:
                dns_list.append(secondary_dns)
            
            is_ipv6 = (address_family.lower() == "ipv6")
            
            success = set_dns_via_windows_api(guid, dns_list, is_ipv6)
            
            if success:
                if not is_ipv6:
                    normalized_primary = (primary_dns or "").strip()
                    if normalized_primary:
                        template = get_doh_template_for_dns(normalized_primary)
                        if template:
                            doh_ok = set_doh_for_adapter(guid, normalized_primary, enable=True)
                            if not doh_ok:
                                log(f"DoH enable failed for {adapter_name}: {normalized_primary}", "WARNING")
                        else:
                            clear_doh_for_adapter(guid)
                            log(f"DoH skipped (no template) for {adapter_name}: {normalized_primary}", "DEBUG")
                notify_dns_change()
                return True, "OK"
            else:
                return False, "Windows DNS API update failed"
            
        except Exception as e:
            return False, str(e)
    
    def set_auto_dns(self, adapter_name: str, address_family: Optional[str] = None) -> Tuple[bool, str]:
        """Сбрасывает DNS на автоматический режим"""
        try:
            guid = self.get_adapter_guid(adapter_name)
            if not guid:
                return False, "GUID not found"
            
            families = ["IPv4", "IPv6"] if address_family is None else [address_family]
            all_ok = True
            
            for family in families:
                is_ipv6 = (family.lower() == "ipv6")
                if not set_dns_via_windows_api(guid, [], is_ipv6):
                    all_ok = False

            if not all_ok:
                return False, "Windows DNS API reset failed"

            if address_family is None or address_family.lower() == "ipv4":
                clear_doh_for_adapter(guid)
            
            notify_dns_change()
            return True, "OK"
            
        except Exception as e:
            return False, str(e)

    def get_doh_info(self, adapter_name: str) -> Dict[str, any]:
        """Получает информацию о DoH для адаптера"""
        guid = self.get_adapter_guid(adapter_name)
        if not guid:
            return {'supported': False, 'enabled': False}
        
        return get_doh_settings_for_adapter(guid)
    
    def set_doh(self, adapter_name: str, dns_ip: str, enable: bool = True) -> Tuple[bool, str]:
        """Включает/выключает DoH для адаптера"""
        try:
            guid = self.get_adapter_guid(adapter_name)
            if not guid:
                return False, "GUID not found"
            
            if not is_doh_supported():
                return False, "DoH not supported on this Windows version"
            
            success = set_doh_for_adapter(guid, dns_ip, enable)
            
            if success:
                return True, "OK"
            else:
                return False, "Failed to set DoH"
                
        except Exception as e:
            return False, str(e)
    
    def clear_doh(self, adapter_name: str) -> Tuple[bool, str]:
        """Очищает настройки DoH для адаптера"""
        try:
            guid = self.get_adapter_guid(adapter_name)
            if not guid:
                return False, "GUID not found"
            
            success = clear_doh_for_adapter(guid)
            return (True, "OK") if success else (False, "Failed")
            
        except Exception as e:
            return False, str(e)
            
    @staticmethod
    def flush_dns_cache() -> Tuple[bool, str]:
        """Очищает DNS кэш"""
        success = flush_dns_cache_native()
        return (success, "OK" if success else "Failed")
