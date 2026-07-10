"""Kolleksiya ko'rish va gacha (karta tortish)."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile, InputMediaPhoto

from database.db import async_session
from database import crud
from game_logic.gacha_engine import roll_gacha
from image_generator.card_renderer import render_card
from bot.keyboards.user_kb import rarity_filter_kb, collection_nav_kb

router = Router(name="cards")

GACHA_COST_GEMS = 30


@router.message(F.text == "🎰 Karta tortish")
async def gacha_pull(message: Message):
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, message.from_user.id)
        if not user:
            await message.answer("Iltimos, avval /start bosing.")
            return

        if user.gems < GACHA_COST_GEMS:
            await message.answer(
                f"❌ Yetarli gems yo'q. Kerak: {GACHA_COST_GEMS} 💎\n"
                f"Sizda: {user.gems} 💎\n\n"
                f"💎 Do'kon orqali gems sotib oling."
            )
            return

        ok = await crud.adjust_gems(session, user, -GACHA_COST_GEMS, "gacha", "Karta tortish")
        if not ok:
            await message.answer("❌ Xatolik yuz berdi, qayta urinib ko'ring.")
            return

        card = await roll_gacha(session)
        if not card:
            # Gems qaytariladi — karta havzasi bo'sh bo'lsa foydalanuvchi jabr chekmasligi kerak
            await crud.adjust_gems(session, user, GACHA_COST_GEMS, "gacha_refund", "Karta havzasi bo'sh")
            await message.answer("😔 Hozircha kartalar mavjud emas. Gems qaytarildi.")
            return

        await crud.add_card_to_user(session, user, card)

    rarity_emoji = {"common": "⚪", "rare": "🔵", "epic": "🟣", "legendary": "🟡", "mythic": "🌈"}
    emoji = rarity_emoji.get(card.rarity, "⚪")

    try:
        png_bytes = render_card(card)
        photo = BufferedInputFile(png_bytes, filename="card.png")
        await message.answer_photo(
            photo,
            caption=f"{emoji} <b>{card.name}</b> ({card.rarity.upper()}) ni qo'lga kiritdingiz!",
            parse_mode="HTML",
        )
    except Exception:
        # Rasm generatsiya muvaffaqiyatsiz bo'lsa ham foydalanuvchi kartasiz qolmasligi kerak
        await message.answer(
            f"{emoji} <b>{card.name}</b> ({card.rarity.upper()}) ni qo'lga kiritdingiz!\n"
            f"ATK:{card.atk} HP:{card.hp} SPD:{card.spd}",
            parse_mode="HTML",
        )


@router.message(F.text == "🎴 Kartalarim")
async def show_collection_menu(message: Message):
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, message.from_user.id)
        if not user:
            await message.answer("Iltimos, avval /start bosing.")
            return
        collection = await crud.get_user_collection(session, user)

    if not collection:
        await message.answer("Sizda hali kartalar yo'q. 🎰 Karta tortish orqali boshlang!")
        return

    await message.answer(
        f"🎴 Sizda jami {len(collection)} ta karta bor.\nFiltrlash uchun tanlang:",
        reply_markup=rarity_filter_kb(),
    )


@router.callback_query(F.data.startswith("cards_filter:"))
async def filter_collection(callback: CallbackQuery):
    rarity = callback.data.split(":")[1]
    rarity = None if rarity == "all" else rarity

    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
        collection = await crud.get_user_collection(session, user, rarity=rarity)

    if not collection:
        await callback.answer("Bu toifada karta topilmadi", show_alert=True)
        return

    await _send_card_at_index(callback, collection, 0, rarity or "all")
    await callback.answer()


@router.callback_query(F.data.startswith("cards_nav:"))
async def navigate_collection(callback: CallbackQuery):
    _, rarity_filter, index_str = callback.data.split(":")
    index = int(index_str)
    rarity = None if rarity_filter == "all" else rarity_filter

    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
        collection = await crud.get_user_collection(session, user, rarity=rarity)

    if index < 0 or index >= len(collection):
        await callback.answer()
        return

    await _send_card_at_index(callback, collection, index, rarity_filter, edit=True)
    await callback.answer()


async def _send_card_at_index(callback: CallbackQuery, collection, index, rarity_filter, edit=False):
    uc = collection[index]
    card = uc.card
    caption = (
        f"<b>{card.name}</b> ({card.rarity.upper()})\n"
        f"« {card.anime} »\n"
        f"⚔ ATK:{card.atk}  ❤ HP:{card.hp}  ⚡ SPD:{card.spd}\n"
        f"Karta darajasi: Lv.{uc.level}"
    )
    kb = collection_nav_kb(index, len(collection), rarity_filter)

    try:
        png_bytes = render_card(card)
        photo = BufferedInputFile(png_bytes, filename="card.png")
        if edit:
            media = InputMediaPhoto(media=photo, caption=caption, parse_mode="HTML")
            await callback.message.edit_media(media, reply_markup=kb)
        else:
            await callback.message.answer_photo(photo, caption=caption, parse_mode="HTML", reply_markup=kb)
    except Exception:
        if edit:
            await callback.message.edit_caption(caption=caption, parse_mode="HTML", reply_markup=kb)
        else:
            await callback.message.answer(caption, parse_mode="HTML", reply_markup=kb)
