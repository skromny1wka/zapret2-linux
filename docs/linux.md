# Zapret на Linux

Экспериментальный порт GUI [Zapret](https://github.com/youtubediscord/zapret) для Kali Linux и других Debian-based дистрибутивов.

Windows-версия использует `winws2.exe` + WinDivert. На Linux используется `nfqws2` из [bol-van/zapret2](https://github.com/bol-van/zapret2) и перехват трафика через **nftables + NFQUEUE**.

## Требования

- Kali Linux / Debian / Ubuntu (64-bit)
- Python 3.11+
- Права **root** (NFQUEUE работает только от root)
- Графическая сессия (X11/Wayland) для PyQt6 GUI
- Runtime-данные: папка `ZapretTwo` (bin, lua, lists, json) или полная Windows-сборка

## Быстрая установка

```bash
git clone https://github.com/youtubediscord/zapret.git
cd zapret

# runtime-данные (bin, lua, lists...) — из Windows-сборки ZapretTwo
# положите рядом или укажите путь через --runtime

chmod +x linux/install.sh linux/zapret-gui linux/stop.sh
sudo linux/install.sh --runtime /path/to/ZapretTwo
```

Если `ZapretTwo` лежит рядом с репозиторием:

```bash
sudo linux/install.sh --runtime ../ZapretTwo
```

## Запуск

```bash
sudo linux/zapret-gui
```

Остановка DPI и снятие правил firewall:

```bash
sudo linux/stop.sh
```

## Что работает на Linux

- GUI Zapret 2 (пресеты, профили, оркестратор — с ограничениями)
- Запуск `nfqws2` с теми же preset/Lua-стратегиями
- Автоматическая настройка nftables (порты из `--wf-*` в пресете)
- Списки доменов, hostlist, ipset

## Что не работает / ограничено

| Функция | Статус |
|---------|--------|
| Zapret 1 (`winws.exe`) | не поддерживается |
| WinDivert-фильтры по payload | заменены перехватом по портам |
| Windows tray (Shell_NotifyIcon) | нет native-трея, окно GUI |
| NSSM / Windows-служба | не применимо |
| Autostart через реестр | не применимо |
| Defender / Max blocker | только Windows |
| Inno Setup / автообновление exe | только Windows |

## Структура после установки

```
zapret/
  src/              # исходники GUI
  exe/nfqws2        # бинарник zapret2
  bin/ lua/ lists/  # runtime
  .venv/            # Python-окружение
  linux/
    install.sh
    zapret-gui
    stop.sh
```

## Устранение неполадок

**GUI не стартует**

```bash
sudo linux/install.sh
sudo linux/zapret-gui
```

**DPI не включается**

- запускайте только через `sudo`
- проверьте: `sudo nft list table inet zapret2`
- логи: `logs/zapret_nfqws2_debug_*.log`

**Нет blob-файлов**

Скопируйте `bin/` из Windows-сборки ZapretTwo или переустановите:

```bash
sudo linux/install.sh --runtime /path/to/ZapretTwo
```

## Связанные проекты

- [youtubediscord/zapret](https://github.com/youtubediscord/zapret) — GUI-лаунчер (этот репозиторий)
- [bol-van/zapret2](https://github.com/bol-van/zapret2) — ядро nfqws2
