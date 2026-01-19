# 🚀 Deployment Guide - External Monitor Brightness Control

## Co zostało dodane?

### ✨ Nowe funkcje:
- **Kontrola jasności monitorów zewnętrznych** przez DDC/CI
- **Multi-monitor support** - każdy monitor ma własny suwak
- **Auto-detection** - monitory wykrywane automatycznie
- **Cache z TTL 30s** - wydajne wykrywanie bez opóźnień
- **Graceful degradation** - applet działa nawet jeśli DDC nie jest dostępny

### 📁 Nowe pliki:
- `backend/ddc_monitor.py` - moduł DDC/CI wrapper dla ddcutil
- `scripts/update_backend.sh` - skrypt aktualizacji backendu
- `test_ddc_integration.py` - testy integracji

### 📝 Zmodyfikowane pliki:
- `backend/legion_power_service.py` - dodane metody D-Bus dla DDC
- `applet.js` - dodana klasa MonitorBrightnessSlider i setup
- `settings-schema.json` - dodana opcja show-external-monitors
- `INSTALL.md` - dokumentacja DDC/CI
- `README.md` - opis nowych funkcji

## 🔧 Jak zaktualizować działający system?

### Krok 1: Zaktualizuj backend (wymaga sudo)

```bash
cd path/to/legion-power-toolkit
sudo ./scripts/update_backend.sh
```

To skopiuje nowe pliki backendu i zrestartuje serwis.

### Krok 2: Zaktualizuj applet

Skopiuj zaktualizowany applet do katalogu Cinnamon:

```bash
# Znajdź gdzie jest zainstalowany applet
APPLET_DIR="$HOME/.local/share/cinnamon/applets/legion-power@moodliszka"

# Jeśli istnieje, zaktualizuj
if [ -d "$APPLET_DIR" ]; then
    cp -r applet/legion-power@moodliszka/files/legion-power@moodliszka/* "$APPLET_DIR/"
    echo "✅ Applet zaktualizowany"
else
    echo "❌ Applet nie znaleziony - zainstaluj przez system settings"
fi
```

### Krok 3: Przeładuj Cinnamon

**Metoda 1 - Restart Cinnamon (szybka):**
- Naciśnij `Alt + F2`
- Wpisz `r`
- Naciśnij `Enter`

**Metoda 2 - Wyloguj się i zaloguj ponownie**

### Krok 4: Włącz kontrolę monitorów

1. Kliknij prawym przyciskiem na ikonę appletu w pasku
2. Wybierz **"Configure..."**
3. Zaznacz **"Show external monitor brightness controls"**
4. Zamknij okno ustawień

### Krok 5: Testuj!

1. Otwórz menu appletu (klik na ikonę)
2. Powinieneś zobaczyć nową sekcję **"External Monitors"**
3. Dla każdego monitora zobaczysz suwak z nazwą (np. "IVM PL2745Q")
4. Przesuwaj suwak - jasność zmienia się w czasie rzeczywistym!

## 🧪 Weryfikacja

### Test 1: Sprawdź czy backend wykrywa monitory

```bash
cd path/to/legion-power-toolkit
python3 test_ddc_integration.py
```

Powinno pokazać:
```
✅ Direct DDC:      ✅ PASS
✅ D-Bus Service:   ✅ PASS

🎉 All tests passed! The applet should work.
```

### Test 2: Sprawdź logi serwisu

```bash
journalctl -u legion-power.service -f
```

W logach powinieneś zobaczyć:
```
INFO - DDC monitor controller initialized
INFO - Detected X monitor(s)
```

### Test 3: Sprawdź ddcutil ręcznie

```bash
ddcutil detect                    # Wykryj monitory
ddcutil -d 1 getvcp 10           # Odczytaj jasność
ddcutil -d 1 setvcp 10 50        # Ustaw jasność na 50%
```

## 🐛 Troubleshooting

### Problem: "No external monitors detected"

**Przyczyna:** ddcutil nie wykrywa monitorów

**Rozwiązanie:**
```bash
# 1. Sprawdź czy ddcutil jest zainstalowany
which ddcutil

# 2. Sprawdź czy wykrywa ręcznie
ddcutil detect

# 3. Sprawdź uprawnienia i2c
groups | grep i2c

# 4. Jeśli nie ma grupy i2c, dodaj się:
sudo usermod -aG i2c $USER
# Potem wyloguj się i zaloguj ponownie!

# 5. Sprawdź czy monitor wspiera DDC/CI
# W OSD monitora włącz DDC/CI support
```

### Problem: "GetExternalMonitors: method not found"

**Przyczyna:** Backend używa starego kodu

**Rozwiązanie:**
```bash
cd path/to/legion-power-toolkit
sudo ./scripts/update_backend.sh
```

### Problem: Monitor wykryty ale nie można zmienić jasności

**Przyczyna:** Monitor nie odpowiada na komendy DDC lub timeout

**Rozwiązanie:**
```bash
# 1. Sprawdź ręcznie czy działa
ddcutil -d 1 setvcp 10 80

# 2. Zwiększ timeout (jeśli wolny monitor)
# Edytuj backend/ddc_monitor.py:
# DDCUTIL_TIMEOUT = 10  # zamiast 5

# 3. Sprawdź logi
journalctl -u legion-power.service -n 50
```

### Problem: Applet nie pokazuje sekcji monitorów

**Przyczyna:** Ustawienie wyłączone lub backend nie działa

**Sprawdź:**
1. Czy w Configure jest zaznaczone "Show external monitor brightness controls"?
2. Czy backend działa: `systemctl status legion-power.service`
3. Czy test przechodzi: `python3 test_ddc_integration.py`

### Problem: Suwaki się nie przesuwają płynnie

**Przyczyna:** ddcutil jest wolny (może trwać 0.5-1s na komendę)

**To normalne!** DDC/CI przez I2C jest wolny. Możesz:
- Zmniejszyć --sleep-multiplier w ddcutil (zaawansowane)
- Użyć --noverify przy setvcp (ryzykowne)

## 📊 Struktura implementacji

```
Backend (Python D-Bus Service)
├── ddc_monitor.py
│   ├── DDCController - główna klasa
│   │   ├── detect_monitors() - wykrywa monitory
│   │   ├── get_brightness() - odczyt VCP 0x10
│   │   └── set_brightness() - zapis VCP 0x10
│   └── DDCMonitor - dataclass reprezentujący monitor
│
└── legion_power_service.py
    ├── GetExternalMonitors() - zwraca listę monitorów
    ├── GetMonitorBrightness(id) - pobiera jasność
    ├── SetMonitorBrightness(id, value) - ustawia jasność
    └── MonitorBrightnessChanged - sygnał D-Bus

Frontend (JavaScript Cinnamon Applet)
└── applet.js
    ├── MonitorBrightnessSlider - klasa suwaka
    │   ├── _getBrightness() - pobiera przez D-Bus
    │   ├── _setBrightness() - ustawia przez D-Bus
    │   └── _onScrollEvent() - obsługa scroll
    │
    └── LegionPowerApplet
        ├── _setupExternalMonitors() - tworzy suwaki
        └── _refreshExternalMonitors() - odświeża co 30s
```

## 🎯 Funkcje zaawansowane

### Cache z TTL
Monitor list jest cache'owany przez 30 sekund. Aby wymusić odświeżenie:
```python
# W Python (przez D-Bus)
interface.RefreshExternalMonitors()
```

### Wiele monitorów
Każdy monitor ma swój własny:
- Display ID (1, 2, 3...)
- I2C bus (/dev/i2c-X)
- Suwak w menu

### Auto-refresh
Jasność jest automatycznie odświeżana co 30 sekund (w przypadku zmian z OSD monitora).

## 📚 Dodatkowe zasoby

- [ddcutil documentation](https://www.ddcutil.com/)
- [DDC/CI specification](https://en.wikipedia.org/wiki/Display_Data_Channel)
- [D-Bus specification](https://dbus.freedesktop.org/doc/dbus-specification.html)

## 🎉 Gotowe!

Po wykonaniu wszystkich kroków powinieneś mieć w pełni działającą kontrolę jasności monitorów zewnętrznych!

Jeśli masz problemy:
1. Uruchom `python3 test_ddc_integration.py`
2. Sprawdź logi: `journalctl -u legion-power.service -f`
3. Sprawdź ddcutil ręcznie: `ddcutil detect`

**Miłego korzystania! 🖥️✨**
