from aiogram import Router, F
from aiogram.types import Message

from bot import database as db
from bot.config import DAILY_BONUS_GEMS

router = Router()


@router.message(F.text == "🎁 Kunlik bonus")
async def claim_daily(message: Message) -> None:
    user_id = message.from_user.id
    user = await db.get_user(user_id)

    if user is None:
        await message.answer("Avval /start buyrug'ini bosing.")
        return

    if user["is_blocked"]:
        await message.answer("Sizning akkountingiz bloklangan.")
        return

    # Serverdagi sana asosida tekshiriladi — client vaqtiga ishonilmaydi,
    # shuning uchun soatni orqaga surib bir necha marta bonus olib
    # bo'lmaydi.
    can_claim = await db.can_claim_daily(user_id)
    if not can_claim:
        await message.answer(
            "Bugungi kunlik bonusni allaqachon oldingiz. Ertaga qayta urinib ko'ring."
        )
        return

    await db.add_gems(user_id, DAILY_BONUS_GEMS, reason="daily_bonus")
    await db.set_daily_claimed(user_id)

    await message.answer(
        f"🎁 Kunlik bonusingiz: +{DAILY_BONUS_GEMS} gems!\n"
        "Ertaga yana qaytib keling."
    )
