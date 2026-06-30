# DM40 Wireless

Desktopová aplikace pro Windows, která přes Bluetooth Low Energy (BLE) ovládá a zobrazuje měření z bezdrátového multimetru **Alientek DM40** (modely DM40A, DM40B, DM40C). Rozhraní napodobuje displej přístroje včetně režimů měření, rozsahů, HOLD a ukládání hodnot.

**Repozitář:** [github.com/Urobotos/DM40-Wireless](https://github.com/Urobotos/DM40-Wireless)

| Větev | Účel |
|-------|------|
| `main` | Stabilní verze odpovídající GitHub Releases |
| `develop` | Aktivní vývoj, nové funkce a opravy |

---

## Požadavky

- **Windows 10/11** s funkčním Bluetooth (BLE)
- Multimetr **Alientek DM40** (A / B / C) v dosahu
- Pro spuštění ze zdrojového kódu: **Python 3.11+** ([python.org](https://www.python.org/)) — při instalaci zaškrtni *Add python to PATH*

---

## Instalace pro běžné uživatele (bez Pythonu)

1. Na GitHubu otevři [Releases](https://github.com/Urobotos/DM40-Wireless/releases) a stáhni **`DM40-Wireless-win64.zip`**.
2. Rozbal zip do libovolné složky (např. `C:\Programy\DM40 Wireless\`).
3. Spusť **`DM40 Wireless.exe`**.
4. Při prvním spuštění se zobrazí obrazovka **Connect** — vyhledej multimetr, vyber ho v seznamu a klikni **Connect**. MAC adresa se uloží do `settings.json` vedle exe; příště se aplikace rovnou připojí.

> Distribuční balíček obsahuje celou složku `dist\DM40 Wireless` z buildu (exe + knihovny). Nepřesouvej jen samotný `.exe` — musí zůstat vedle podsložky `_internal` a `images`.

---

## Spuštění ze zdrojového kódu (vývojáři)

```bat
git clone -b develop https://github.com/Urobotos/DM40-Wireless.git
cd DM40-Wireless
install.bat
```

Poté spusť jedním z těchto způsobů:

| Způsob | Popis |
|--------|--------|
| **`DM40 Wireless.bat`** | Doporučeno — spustí `app.pyw` bez konzole (přes venv, pokud existuje) |
| **`app.pyw`** | Dvojklik nebo `pythonw app.pyw` — bez konzole |
| **`app.py`** | `python app.py` — s konzolí (ladění, logy) |

Při prvním běhu zkopíruj šablonu nastavení:

```bat
copy settings.example.json settings.json
```

---

## Ovládání aplikace

### Obrazovka Connect (první spuštění / prázdná MAC)

- **Search** — sken BLE zařízení DM40 v okolí
- Klik na řádek v seznamu — výběr zařízení
- **Connect** — uložení MAC a modelu, připojení a přechod na hlavní obrazovku

### Hlavní obrazovka

| Oblast | Akce |
|--------|------|
| **AUTO+** (vlevo nahoře) | Otevře menu **rozsahů** (RANGE) pro aktuální režim |
| **RUN / HOLD** | Přepne držení měřené hodnoty (HOLD) |
| **MODE tlačítka** (řada dole) | Cyklují podrežimy: VDC/VAC, ADC/AAC, OHM, CAP, DIODE/CONT, Hz/TEMP |
| **Hodnota uprostřed** | Klik uloží aktuální měření do prvního volného **save slotu** (max. 6) |
| **Save sloty** | Klik na slot — načtení uložené hodnoty zpět na displej |
| **Graf** | Průběh měření v čase (v režimu Mini app skrytý) |
| **Ikona nastavení** (vpravo nahoře) | Obrazovka **Settings** |

Stav připojení, baterie multimetru a jednotky se zobrazují v horní liště podle reálných dat z BLE.

### Obrazovka RANGE

- Seznam rozsahů pro aktuální měřicí režim (závisí na modelu DM40A/B/C)
- **Back** — návrat na hlavní obrazovku

### Obrazovka Settings

| Přepínač | Funkce |
|----------|--------|
| **Mini app** | Menší okno bez grafu a save slotů |
| **Always on top** | Okno vždy navrchu ostatních aplikací |
| **RAW data console** | Panel pod UI s TX/RX pakety BLE (pro ladění protokolu) |

Změny se ukládají do `settings.json`.

---

## Nastavení (`settings.json`)

Soubor leží vedle exe nebo v kořeni projektu. Do gitu se necommituje — použij `settings.example.json` jako vzor.

| Klíč | Význam |
|------|--------|
| `target_mac` | MAC adresa DM40 (`""` = zobrazit Connect) |
| `model_name` | `DM40A`, `DM40B` nebo `DM40C` |
| `device_counts` | Počet countů rozsahů (40k / 50k / 60k) |
| `window_scale` | Měřítko okna (`1.0` = 480×300 px logicky) |
| `mini_app` | Mini režim |
| `always_on_top` | Vždy navrchu |
| `raw_console` | RAW konzole |

---

## Sestavení exe a release zip (maintainer)

```bat
build_exe.bat
release_zip.bat
```

- **`build_exe.bat`** — PyInstaller `--onedir`, výstup: `dist\DM40 Wireless\`
- **`release_zip.bat`** — vytvoří `release\DM40-Wireless-win64.zip` pro GitHub Release

Při publikaci release na GitHubu:

1. Sestav exe a zip (viz výše).
2. Vytvoř nový Release z větve `main` s tagem např. `v1.0.0`.
3. Přilož asset **`DM40-Wireless-win64.zip`**.
4. Zdrojový kód zůstává v repozitáři; uživatelé stahují zip, vývojáři klonují repo.

---

## Struktura projektu

```
DM40-Wireless/
├── app.py / app.pyw      # Entry point
├── ble/                  # BLE worker, discovery
├── core/                 # Protokol, parsování, režimy
├── gui/                  # Tkinter UI
├── images/               # Grafika rozhraní
├── settings.example.json
├── install.bat
├── build_exe.bat
└── release_zip.bat
```

---

## Licence

Zatím bez explicitní licence — kontaktuj vlastníka repozitáře [Urobotos](https://github.com/Urobotos) před komerčním použitím.

---

## Poznámky

- Aplikace není oficiální produkt Alientek; jde o komunitní / nadšenecký projekt.
- Vyžaduje zapnutý Bluetooth ve Windows; při vypnutém BT se zobrazí upozornění.
