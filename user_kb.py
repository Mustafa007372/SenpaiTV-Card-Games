"""Foydalanuvchi uchun barcha klaviaturalar."""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="🎴 Kartalarim"), KeyboardButton(text="🎰 Karta tortish")],
        [KeyboardButton(text="⚔️ Jang qilish"), KeyboardButton(text="🎁 Kunlik bonus")],
        [KeyboardButton(text="💎 Do'kon"), KeyboardButton(text="👤 Profil")],
        [KeyboardButton(text="☎️ Yordam")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def rarity_filter_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Hammasi", callback_data="cards_filter:all")
    for r in ["common", "rare", "epic", "legendary", "mythic"]:
        builder.button(text=r.capitalize(), callback_data=f"cards_filter:{r}")
    builder.adjust(3)
    return builder.as_markup()


def collection_nav_kb(index: int, total: int, rarity_filter: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if index > 0:
        builder.button(text="⬅️", callback_data=f"cards_nav:{rarity_filter}:{index-1}")
    builder.button(text=f"{index+1}/{total}", callback_data="noop")
    if index < total - 1:
        builder.button(text="➡️", callback_data=f"cards_nav:{rarity_filter}:{index+1}")
    builder.adjust(3)
    return builder.as_markup()


def battle_choose_card_kb(user_cards) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for uc in user_cards[:10]:  # MVP: birinchi 10 ta kartadan tanlash
        builder.button(
            text=f"{uc.card.name} (Lv.{uc.level})",
            callback_data=f"battle_use:{uc.id}",
        )
    builder.adjust(1)
    return builder.as_markup()


def shop_packages_kb(packages: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for stars, gems in packages.items():
        builder.button(text=f"⭐ {stars} Stars → 💎 {gems} gems", callback_data=f"buy_gems:{stars}")
    builder.adjust(1)
    return builder.as_markup()


def support_category_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 To'lov muammosi", callback_data="support_cat:payment")
    builder.button(text="🐞 Bug xatolik", callback_data="support_cat:bug")
    builder.button(text="💡 Taklif", callback_data="support_cat:suggestion")
    builder.button(text="❓ Boshqa", callback_data="support_cat:other")
    builder.adjust(2)
    return builder.as_markup()
