"""
Gacha (kartalar tortish) tizimi.
MUHIM: Ehtimollik hisob-kitobi FAQAT shu yerda, serverda amalga oshadi.
Client (foydalanuvchi) faqat "tort" tugmasini bosadi, natijani hech qachon
o'zi hisoblamaydi va o'zgartira olmaydi.
"""
import random
from sqlalchemy.ext.asyncio import AsyncSession

from database import crud
from database.models import Card
from config import config


async def roll_gacha(session: AsyncSession) -> Card | None:
    """Ehtimolliklarga asoslanib bitta tasodifiy rarity tanlaydi,
    keyin o'sha rarity'dan tasodifiy faol kartani qaytaradi.
    """
    rarities = list(config.GACHA_RATES.keys())
    weights = list(config.GACHA_RATES.values())

    chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]
    pool = await crud.get_active_cards_by_rarity(session, chosen_rarity)

    if not pool:
        # Agar shu rarity'da karta bo'lmasa (masalan hali admin qo'shmagan) — common'ga tushamiz
        pool = await crud.get_active_cards_by_rarity(session, "common")
        if not pool:
            return None

    return random.choice(pool)
