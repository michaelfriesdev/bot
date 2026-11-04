# Minecraft AFK Bot 🤖

Bot łączy się z serwerem Minecraft, stoi nieruchomo 24/7 i automatycznie
reconnectuje się po każdym wyrzuceniu lub rozłączeniu.

---

## Wymagania

| Oprogramowanie | Wersja minimalna |
|---|---|
| Python | 3.8+ |
| Node.js | 18+ |
| npm | 8+ |

---

## Instalacja na VPS (Ubuntu/Debian)

### 1. Zaktualizuj system i zainstaluj zależności

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip curl git
```

### 2. Zainstaluj Node.js 18+

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
node --version   # powinno pokazać v18.x lub nowszy
```

### 3. Skopiuj pliki bota na serwer

```bash
# Lokalnie (z twojego komputera):
scp -r . ubuntu@TWOJ_VPS_IP:/home/ubuntu/minecraft-bot

# Albo przez git:
git clone <url_repo> /home/ubuntu/minecraft-bot
cd /home/ubuntu/minecraft-bot
```

### 4. Zainstaluj zależności Python i Node

```bash
cd /home/ubuntu/minecraft-bot

# Python
pip3 install -r requirements.txt

# Node.js – mineflayer zainstaluje się automatycznie przy pierwszym uruchomieniu
# ale możesz też zainstalować ręcznie:
# npm install mineflayer
```

### 5. Skonfiguruj bota

Edytuj `config.json`:

```json
{
  "host": "mc.twojserwer.pl",
  "port": 25565,
  "username": "NazwaBota",
  "version": "1.20.1",
  "reconnect_delay": 10,
  "reconnect_max_delay": 60,
  "auth": "offline"
}
```

| Pole | Opis |
|---|---|
| `host` | Adres IP lub domena serwera Minecraft |
| `port` | Port serwera (domyślnie 25565) |
| `username` | Nick bota (dla serwerów offline) |
| `version` | Wersja Minecrafta serwera (np. `"1.20.1"`) |
| `auth` | `"offline"` dla serwerów bez premium, `"microsoft"` dla premium |
| `reconnect_delay` | Ile sekund czekać przed pierwszym reconnectem |
| `reconnect_max_delay` | Maksymalny delay reconnectu (backoff) |

---

## Uruchamianie

### Opcja A – jednorazowo (test)

```bash
python3 bot.py
```

### Opcja B – watchdog bash (prosty autostart)

```bash
chmod +x start.sh
./start.sh
```

### Opcja C – systemd (zalecane na VPS, działa 24/7 po restarcie serwera) ⭐

```bash
# Skopiuj plik usługi (zmień ścieżki jeśli potrzeba)
sudo cp minecraft-bot.service /etc/systemd/system/

# Załaduj i uruchom
sudo systemctl daemon-reload
sudo systemctl enable minecraft-bot
sudo systemctl start minecraft-bot

# Sprawdź status
sudo systemctl status minecraft-bot

# Logi na żywo
sudo journalctl -u minecraft-bot -f
```

### Opcja D – screen / tmux (prosta alternatywa)

```bash
# screen
screen -S mcbot
python3 bot.py
# Ctrl+A, D  →  odłącz, bot działa w tle
# screen -r mcbot  →  wróć do sesji

# tmux
tmux new -s mcbot
python3 bot.py
# Ctrl+B, D  →  odłącz
# tmux attach -t mcbot  →  wróć
```

---

## Logi

Bot zapisuje logi do pliku `bot.log` oraz wyświetla je na stdout.

```bash
tail -f bot.log
```

---

## Struktura plików

```
minecraft-bot/
├── bot.py                 # Główny skrypt bota
├── config.json            # Konfiguracja (host, port, nick, itp.)
├── requirements.txt       # Zależności Python
├── start.sh               # Skrypt startowy z watchdogiem
├── minecraft-bot.service  # Plik usługi systemd
├── bot.log                # Logi (tworzy się automatycznie)
└── README.md              # Ta instrukcja
```

---

## Jak działa reconnect

1. Bot łączy się z serwerem.
2. Jeśli zostanie wyrzucony (`kicked`), rozłączy się (`end`) lub wystąpi błąd (`error`) — czeka `reconnect_delay` sekund i łączy się ponownie.
3. Przy każdej nieudanej próbie delay podwaja się (exponential backoff) aż do `reconnect_max_delay`.
4. Po udanym połączeniu delay resetuje się do wartości początkowej.
5. Systemd/start.sh dodatkowo restartuje cały skrypt jeśli Python crashnie.

---

## Serwery premium (konto Microsoft)

Zmień w `config.json`:

```json
"auth": "microsoft"
```

Przy pierwszym uruchomieniu bot wyświetli link do autoryzacji Microsoft w terminalu.
Zaloguj się raz, token zostanie zapisany automatycznie.

---

## Rozwiązywanie problemów

| Problem | Rozwiązanie |
|---|---|
| `ModuleNotFoundError: javascript` | `pip3 install javascript` |
| `node: not found` | Zainstaluj Node.js 18+ (patrz krok 2) |
| Bot ciągle jest wyrzucany | Sprawdź czy serwer wymaga konta premium / captcha |
| `version mismatch` | Zmień `version` w config.json na wersję serwera |
| Bot nie łączy się | Sprawdź `host`, `port` i firewall VPS |
