"""
Admin komandalar. Faqat config.ADMIN_IDS ro'yxatidagilar uchun ishlaydi
(filtr har bir handlerda tekshiriladi — middleware orqali emas,
chunki ba'zi komandalar aralash foydalanuvchi/admin oqimida bo'lishi mumkin).
"""
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import async_session
from database import crud
from bot.keyboards.admin_kb import admin_main_kb, user_manage_kb
from config import config

router = Router(name="admin")


def is_admin(telegram_id: int) -> bool:
    return telegram_id in config.ADMIN_IDS


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return  # oddiy foydalanuvchiga hech narsa ko'rsatilmaydi
    await message.answer("🛠 <b>Admin panel</b>", reply_markup=admin_main_kb(), parse_mode="HTML")


@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    async with async_session() as session:
        total = await crud.get_total_users(session)
        active_24h = await crud.get_active_users_since(session, 24)

    await callback.message.answer(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchi: {total}\n"
        f"🟢 24 soatda faol: {active_24h}\n",
        parse_mode="HTML",
    )
    await callback.answer()


class AdminStates(StatesGroup):
    waiting_search_query = State()
    waiting_broadcast_text = State()
    waiting_card_data = State()


@router.callback_query(F.data == "admin:search_user")
async def start_search(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.set_state(AdminStates.waiting_search_query)
    await callback.message.answer("🔍 Telegram ID yoki username kiriting:")
    await callback.answer()


@router.message(AdminStates.waiting_search_query)
async def do_search(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    async with async_session() as session:
        user = await crud.search_user(session, message.text.strip())

    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi.")
        await state.clear()
        return

    blocked_label = "Ha" if user.is_blocked else "Yo'q"
    text = (
        f"👤 {user.full_name} (@{user.username or '—'})\n"
        f"ID: {user.telegram_id}\n"
        f"💎 Gems: {user.gems} | 🪙 Coins: {user.coins}\n"
        f"📊 Daraja: {user.level}\n"
        f"⚔️ W/L: {user.wins}/{user.losses}\n"
        f"🚫 Bloklangan: {blocked_label}"
    )
    await message.answer(text, reply_markup=user_manage_kb(user.telegram_id, user.is_blocked))
    await state.clear()


@router.callback_query(F.data.startswith("admin:toggle_block:"))
async def toggle_block(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    telegram_id = int(callback.data.split(":")[2])
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, telegram_id)
        if user:
            user.is_blocked = not user.is_blocked
            await session.commit()
            status = "bloklandi" if user.is_blocked else "blokdan chiqarildi"
            await callback.answer(f"Foydalanuvchi {status}", show_alert=True)


@router.callback_query(F.data.startswith("admin:grant_gems:"))
async def grant_gems(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    _, _, telegram_id_str, amount_str = callback.data.split(":")
    telegram_id, amount = int(telegram_id_str), int(amount_str)

    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, telegram_id)
        if user:
            await crud.adjust_gems(session, user, amount, "admin_grant", f"Admin tomonidan berildi ({callback.from_user.id})")
            await callback.answer(f"+{amount} gems berildi", show_alert=True)


@router.callback_query(F.data == "admin:broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.set_state(AdminStates.waiting_broadcast_text)
    await callback.message.answer("📢 Barcha foydalanuvchilarga yuboriladigan xabarni yozing:")
    await callback.answer()


@router.message(AdminStates.waiting_broadcast_text)
async def do_broadcast(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    async with async_session() as session:
        ids = await crud.get_all_user_telegram_ids(session)

    sent, failed = 0, 0
    for tg_id in ids:
        try:
            await bot.send_message(tg_id, message.text)
            sent += 1
        except Exception:
            failed += 1

    await message.answer(f"📢 Broadcast tugadi.\n✅ Yuborildi: {sent}\n❌ Xatolik: {failed}")
    await state.clear()


@router.callback_query(F.data == "admin:add_card")
async def start_add_card(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.set_state(AdminStates.waiting_card_data)
    await callback.message.answer(
        "🃏 Yangi karta ma'lumotlarini shu formatda yuboring:\n\n"
        "<code>Nom | Anime | rarity | atk | hp | spd | qobiliyat_nomi | qobiliyat_tavsifi</code>\n\n"
        "Masalan:\n"
        "<code>Naruto | Naruto | rare | 45 | 120 | 30 | Rasengan | Dushmanga kuchli zarba beradi</code>",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(AdminStates.waiting_card_data)
async def do_add_card(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    try:
        parts = [p.strip() for p in message.text.split("|")]
        name, anime, rarity, atk, hp, spd, ability_name, ability_desc = parts
        rarity = rarity.lower()
        if rarity not in config.GACHA_RATES:
            raise ValueError(f"Noto'g'ri rarity: {rarity}")

        async with async_session() as session:
            card = await crud.create_card(
                session,
                name=name, anime=anime, rarity=rarity,
                atk=int(atk), hp=int(hp), spd=int(spd),
                ability_name=ability_name, ability_desc=ability_desc,
            )
        await message.answer(f"✅ Karta yaratildi: {card.name} (ID: {card.id})")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}\n\nQaytadan to'g'ri formatda yuboring yoki /admin bilan bekor qiling.")
        return

    await state.clear()


@router.message(Command("reply"))
async def admin_reply(message: Message, bot: Bot):
    """Foydalanuvchiga support xabariga javob: /reply <telegram_id> <matn>"""
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Format: /reply <telegram_id> <xabar matni>")
        return

    try:
        target_id = int(parts[1])
        reply_text = parts[2]
        await bot.send_message(
            target_id,
            f"☎️ <b>Admin javobi:</b>\n\n{reply_text}",
            parse_mode="HTML",
        )
        await message.answer("✅ Javob yuborildi.")
    except Exception as e:
        await message.answer(f"❌ Yuborilmadi: {e}")
