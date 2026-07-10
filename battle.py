"""PvE jang oqimi."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database.db import async_session
from database import crud
from game_logic.battle_engine import simulate_battle
from bot.keyboards.user_kb import battle_choose_card_kb

router = Router(name="battle")


@router.message(F.text == "⚔️ Jang qilish")
async def battle_menu(message: Message):
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, message.from_user.id)
        if not user:
            await message.answer("Iltimos, avval /start bosing.")
            return
        collection = await crud.get_user_collection(session, user)

    if not collection:
        await message.answer("Jang qilish uchun avval 🎰 Karta tortish orqali karta oling!")
        return

    await message.answer(
        "⚔️ Jang uchun kartangizni tanlang:",
        reply_markup=battle_choose_card_kb(collection),
    )


@router.callback_query(F.data.startswith("battle_use:"))
async def do_battle(callback: CallbackQuery):
    user_card_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
        collection = await crud.get_user_collection(session, user)
        uc = next((c for c in collection if c.id == user_card_id), None)

        if not uc:
            await callback.answer("Karta topilmadi", show_alert=True)
            return

        result = simulate_battle(uc.card, user.level)

        if result.win:
            user.wins += 1
        else:
            user.losses += 1
        await crud.adjust_gems(session, user, result.reward_gems, "battle_reward", "PvE jang natijasi")

    text = "\n".join(result.log)
    text += f"\n\n💎 Mukofot: +{result.reward_gems} gems"
    await callback.message.edit_text(text)
    await callback.answer()
