<h1 align="center">
  <a href="https://github.com/bol-van/zapret2">Zapret 2</a> — Linux-порт
</h1>

<p align="center">
  <strong>Форк GUI-лаунчера <a href="https://github.com/youtubediscord/zapret">youtubediscord/zapret</a> для Kali Linux, Debian и Ubuntu</strong>
</p>

<p align="center">
  <a href="https://github.com/skromny1wka/zapret2-linux"><img alt="Репозиторий" src="https://img.shields.io/badge/репозиторий-zapret2--linux-181717?style=flat-square&logo=github"></a>
  <a href="https://github.com/youtubediscord/zapret"><img alt="Upstream" src="https://img.shields.io/badge/upstream-youtubediscord%2Fzapret-2CA5E0?style=flat-square&logo=github"></a>
  <a href="docs/linux.md"><img alt="Документация Linux" src="https://img.shields.io/badge/docs-linux.md-7C3AED?style=flat-square"></a>
</p>

---

## Что это

**zapret2-linux** — неофициальный форк популярного GUI [Zapret](https://github.com/youtubediscord/zapret) с поддержкой **Linux**.

Оригинал рассчитан на Windows (`winws2.exe` + WinDivert). Здесь добавлен экспериментальный порт под Linux:

| Windows (оригинал) | Linux (этот форк) |
|--------------------|-------------------|
| `winws2.exe` | `nfqws2` из [bol-van/zapret2](https://github.com/bol-van/zapret2) |
| WinDivert | **nftables + NFQUEUE** |
| Права администратора (UAC) | **root** (`sudo`) |
| Inno Setup / `.exe` | `linux/install.sh` + Python venv |

Сохранены те же пресеты, Lua-стратегии, профили и GUI PyQt6. Runtime-данные (`bin/`, `lua/`, `lists/`) берутся из сборки **ZapretTwo** (Windows-пакет).

### Дополнительно в форке

- **Автообновление реестра РКН/DPI** раз в час — `lists/russia-blacklist.txt` и `lists/base/ipset-all.txt` подтягиваются из открытых источников ([Re-filter](https://github.com/1andrevich/Re-filter-lists), [antifilter.download](https://antifilter.download)); при изменении списков DPI перезапускается автоматически.

---

## Требования

- Kali Linux / Debian / Ubuntu (64-bit)
- Python 3.11+
- Графическая сессия (X11 / Wayland) для GUI
- Права **root** (NFQUEUE и nftables)
- Папка **ZapretTwo** с runtime: `bin/`, `lua/`, `lists/`, `json/`, пресеты

---

## Установка

```bash
git clone https://github.com/skromny1wka/zapret2-linux.git
cd zapret2-linux

chmod +x linux/install.sh linux/zapret-gui linux/stop.sh linux/rkn-sync.sh

# рекомендуется: быстрый режим (без apt update, без blob, PyQt6 из apt)
sudo linux/install.sh --fast --runtime /path/to/ZapretTwo
```

Если `ZapretTwo` лежит рядом с репозиторием:

```bash
sudo linux/install.sh --runtime ../ZapretTwo
```

Установщик:

- ставит системные пакеты (`nftables`, Python, PyQt6 и зав.),
- скачивает `nfqws2` из [bol-van/zapret2](https://github.com/bol-van/zapret2),
- копирует runtime из `ZapretTwo`,
- создаёт venv и launcher.

---

## Запуск

```bash
sudo linux/zapret-gui
```

В GUI выберите **Zapret 2**, нужный пресет и нажмите **Старт**.

Остановка:

```bash
sudo linux/stop.sh
```

Если `apt-get update` зависает на «ожидании заголовков», см. [docs/linux.md](docs/linux.md#устранение-неполадок).

Ручное обновление списков РКН:

```bash
linux/rkn-sync.sh
linux/rkn-sync.sh --force
```

---

## Что работает / не работает

**Работает**

- GUI Zapret 2, пресеты, профили, hostlist/ipset
- `nfqws2` + nftables
- Оркестратор (с ограничениями)
- Автообновление реестра РКН/DPI

**Не работает или ограничено**

- Zapret 1 (`winws.exe`)
- WinDivert-фильтры по payload (заменены перехватом по портам)
- Windows tray, NSSM, autostart через реестр
- Defender / Max blocker, Inno Setup / автообновление `.exe`

Подробнее: [docs/linux.md](docs/linux.md)

---

## Структура

```
zapret2-linux/
  src/                 # исходники GUI (форк upstream)
  linux/
    install.sh         # установщик
    zapret-gui         # launcher GUI
    stop.sh            # остановка DPI
    rkn-sync.sh        # обновление списков РКН
  docs/linux.md        # полная документация
  exe/nfqws2           # появляется после install.sh
  bin/ lua/ lists/     # копируются из ZapretTwo
```

---

## Связанные проекты

- [youtubediscord/zapret](https://github.com/youtubediscord/zapret) — оригинальный GUI (Windows)
- [bol-van/zapret2](https://github.com/bol-van/zapret2) — ядро `nfqws2`
- [1andrevich/Re-filter-lists](https://github.com/1andrevich/Re-filter-lists) — источник списков РКН

---

## Лицензия и ответственность

Код основан на [youtubediscord/zapret](https://github.com/youtubediscord/zapret). Linux-порт — экспериментальный; используйте на свой риск. Вопросы по форку — в [Issues](https://github.com/skromny1wka/zapret2-linux/issues) этого репозитория.
