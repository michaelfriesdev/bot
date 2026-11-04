"""
Minecraft AFK Bot
=================
Łączy się z serwerem Minecraft, stoi nieruchomo i automatycznie
reconnectuje się po wyrzuceniu lub rozłączeniu.

Wymagania:
  pip install javascript
  Node.js 18+
"""

import json
import time
import logging
import signal
import sys
from javascript import require, On, off

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("MCBot")

# ── Konfiguracja ───────────────────────────────────────────────────────────
def load_config(path: str = "config.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ── Mineflayer (Node.js przez JSPyBridge) ─────────────────────────────────
mineflayer = require("mineflayer")

# ── Stan bota ──────────────────────────────────────────────────────────────
bot = None
reconnect_delay = 10       # sekundy do pierwszego retry
reconnect_attempt = 0
running = True             # flaga głównej pętli


def create_bot(cfg: dict):
    """Tworzy nową instancję bota mineflayer."""
    global bot, reconnect_delay, reconnect_attempt

    reconnect_attempt += 1
    log.info(f"Próba połączenia #{reconnect_attempt} → {cfg['host']}:{cfg['port']} jako '{cfg['username']}'")

    bot = mineflayer.createBot({
        "host":     cfg["host"],
        "port":     cfg["port"],
        "username": cfg["username"],
        "version":  cfg["version"],
        "auth":     cfg.get("auth", "offline"),
        # Wyłącz zbieranie bloków / walka – tylko stanie
        "checkTimeoutInterval": 60_000,   # ms
    })

    # ── Zdarzenia ──────────────────────────────────────────────────────────

    @On(bot, "login")
    def on_login(*args):
        global reconnect_delay, reconnect_attempt
        reconnect_delay = cfg.get("reconnect_delay", 10)   # reset delay po sukcesie
        reconnect_attempt = 0
        log.info(f"✅ Zalogowano! Pozycja startowa: {bot.entity.position}")

    @On(bot, "spawn")
    def on_spawn(*args):
        log.info("🟢 Bot zspawnowany na serwerze – stoi nieruchomo.")
        # Nic nie robimy – bot tylko stoi.

    @On(bot, "chat")
    def on_chat(this, username, message, *args):
        if username == bot.username:
            return
        log.info(f"💬 <{username}> {message}")

    @On(bot, "kicked")
    def on_kicked(this, reason, *args):
        log.warning(f"🚫 Bot wyrzucony. Powód: {reason}")
        schedule_reconnect(cfg)

    @On(bot, "error")
    def on_error(this, err, *args):
        log.error(f"❌ Błąd: {err}")
        schedule_reconnect(cfg)

    @On(bot, "end")
    def on_end(this, reason, *args):
        log.warning(f"🔌 Połączenie zakończone. Powód: {reason}")
        schedule_reconnect(cfg)


def schedule_reconnect(cfg: dict):
    """Czeka przez narastający delay i tworzy nowego bota."""
    global reconnect_delay

    if not running:
        return

    max_delay = cfg.get("reconnect_max_delay", 60)
    log.info(f"⏳ Reconnect za {reconnect_delay}s …")
    time.sleep(reconnect_delay)

    # Exponential backoff z limitem
    reconnect_delay = min(reconnect_delay * 2, max_delay)

    create_bot(cfg)


def graceful_exit(sig, frame):
    """Obsługa Ctrl+C / SIGTERM."""
    global running
    running = False
    log.info("🛑 Zamykanie bota …")
    if bot:
        try:
            bot.quit()
        except Exception:
            pass
    sys.exit(0)


# ── Wejście ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    signal.signal(signal.SIGINT,  graceful_exit)
    signal.signal(signal.SIGTERM, graceful_exit)

    cfg = load_config("config.json")
    log.info("🚀 Uruchamiam Minecraft AFK Bot …")
    log.info(f"   Serwer  : {cfg['host']}:{cfg['port']}")
    log.info(f"   Nick    : {cfg['username']}")
    log.info(f"   Wersja  : {cfg['version']}")

    create_bot(cfg)

    # Główna pętla – trzyma proces przy życiu
    while running:
        time.sleep(1)
