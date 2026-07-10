"""
Konfiguratsiya fayli.
Barcha maxfiy ma'lumotlar (.env) shu yerdan o'qiladi — kodga hardcode qilinmaydi.
"""
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: list[int] = field(default_factory=lambda: [
        int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()
    ])
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///tcg_bot.db")

    # O'yin sozlamalari (F1 — MVP uchun oddiy qat'iy qiymatlar,
    # keyinchalik admin panel orqali o'zgartiriladigan bo'ladi — F2)
    DAILY_GACHA_COOLDOWN_HOURS: int = 24
    STARTING_GEMS: int = 100
    REFERRAL_BONUS_GEMS: int = 50
    REFERRAL_DAILY_LIMIT: int = 5          # bitta user kuniga max 5 ta referral hisoblanadi

    # Gacha ehtimolliklari (rarity: foiz) — yig'indisi 100 bo'lishi shart
    GACHA_RATES: dict = field(default_factory=lambda: {
        "common": 55,
        "rare": 27,
        "epic": 12,
        "legendary": 5,
        "mythic": 1,
    })

    # Stars narxlari (Telegram Stars) -> gems miqdori
    STARS_PACKAGES: dict = field(default_factory=lambda: {
        50: 100,     # 50 Stars -> 100 gems
        100: 220,    # 100 Stars -> 220 gems (bonus)
        250: 600,    # 250 Stars -> 600 gems (yaxshiroq bonus)
    })

    # Rate limiting
    THROTTLE_RATE_LIMIT: float = 0.7  # soniya


config = Config()
