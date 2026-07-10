import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

ADMIN_IDS = {
    int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()
}

DAILY_BONUS_GEMS = int(os.getenv("DAILY_BONUS_GEMS", "10"))
REFERRAL_BONUS_GEMS = int(os.getenv("REFERRAL_BONUS_GEMS", "20"))
GACHA_COST_GEMS = int(os.getenv("GACHA_COST_GEMS", "50"))

DB_PATH = os.getenv("DB_PATH", "database.db")

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN topilmadi. .env faylini yarating va BOT_TOKEN qiymatini kiriting "
        "(.env.example faylidan nusxa oling)."
    )
