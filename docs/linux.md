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
git clone https://github.com/skromny1wka/zapret2-linux.git
cd zapret2-linux

# runtime-данные (bin, lua, lists...) — из Windows-сборки ZapretTwo
# положите рядом или укажите путь через --runtime

chmod +x linux/install.sh linux/zapret-gui linux/stop.sh linux/rkn-sync.sh
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
- **Автообновление реестра РКН/DPI** раз в час (`lists/russia-blacklist.txt`, `lists/base/ipset-all.txt`)

## Автообновление реестра РКН

GUI автоматически (раз в час):

1. Скачивает домены из открытых реестров РКН и DPI-списков ([Re-filter](https://github.com/1andrevich/Re-filter-lists), [antifilter.download](https://antifilter.download))
2. Обновляет `lists/russia-blacklist.txt` — используется пресетами Zapret 2
3. Обновляет `lists/base/ipset-all.txt` — IP/CIDR из реестра
4. Для новых доменов выполняет DNS-резолв (до 400 адресов за цикл)
5. Если DPI уже запущен — перезапускает `nfqws2` для применения списков

Ручной запуск на Linux:

```bash
linux/rkn-sync.sh
linux/rkn-sync.sh --force
```

Настройки (в `settings/settings.json`):

- `program.rkn_lists_auto_update_enabled` — включить/выключить (по умолчанию `true`)
- `program.rkn_lists_auto_update_interval_sec` — интервал в секундах (по умолчанию `3600`)

Состояние последней синхронизации: `lists/.rkn_sync_state.json`


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

- [youtubediscord/zapret](https://github.com/youtubediscord/zapret) — оригинальный GUI (Windows)
- [skromny1wka/zapret2-linux](https://github.com/skromny1wka/zapret2-linux) — этот Linux-форк
- [bol-van/zapret2](https://github.com/bol-van/zapret2) — ядро nfqws2
