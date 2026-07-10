"""Kunlik bepul bonus."""
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import Message

from database.db import async_session
from database import crud
from config import config

router = Router(name="daily")


@router.message(F.text == "🎁 Kunlik bonus")
async def daily_bonus(message: Message):
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, message.from_user.id)
        if not user:
            await message.answer("Iltimos, avval /start bosing.")
            return

        if not await crud.can_claim_daily(user):
            remaining = (
                user.last_daily_claim + timedelta(hours=config.DAILY_GACHA_COOLDOWN_HOURS)
            ) - datetime.utcnow()
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            await message.answer(
                f"⏳ Kunlik bonusni allaqachon oldingiz.\n"
                f"Keyingisi: {hours} soat {minutes} daqiqadan keyin."
            )
            return

        bonus = await crud.claim_daily(session, user)

    await message.answer(
        f"🎁 Kunlik bonus olindi!\n"
        f"💎 +{bonus} gems\n"
        f"🔥 Streak: {user.daily_streak} kun\n\n"
        f"Har kuni kirib, streak'ingizni oshiring — bonus kattalashadi!"
    )
