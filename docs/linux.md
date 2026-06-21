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

**Одной командой** (зеркало apt для РФ + зависимости + Zapret):

```bash
curl -fsSL https://raw.githubusercontent.com/skromny1wka/zapret2-linux/main/linux/install-all.sh -o /tmp/install-all.sh
chmod +x /tmp/install-all.sh
sudo /tmp/install-all.sh --runtime /path/to/ZapretTwo
```

Или из клонированного репозитория:

```bash
git clone https://github.com/skromny1wka/zapret2-linux.git
cd zapret2-linux
chmod +x linux/install-all.sh
sudo linux/install-all.sh --runtime ../ZapretTwo
```

Ручная установка (без apt в install.sh):

```bash
git clone https://github.com/skromny1wka/zapret2-linux.git
cd zapret2-linux

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

**Установка зависла на «Ожидание заголовков» / 0%**

Чаще всего это `apt-get update` или `pip install PyQt6` (долго показывает 0%).

```bash
cd zapret2-linux
git pull

# рекомендуемый быстрый режим
sudo linux/install.sh --fast --runtime /path/to/ZapretTwo
```

Что делает `--fast`:
- не вызывает `apt-get update`
- не качает blob из GitHub (берёт из ZapretTwo/bin)
- ставит **PyQt6 из apt**, а не через pip

Если apt тоже тормозит:

```bash
sudo apt install -y python3 python3-venv python3-pyqt6 nftables curl
sudo linux/install.sh --skip-apt --skip-blobs --runtime ../ZapretTwo
```

Установщик печатает шаги `========== 1/7 ... ==========` — смотрите, на каком шаге остановилось.

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
