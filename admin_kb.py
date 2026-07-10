"""Admin uchun klaviaturalar (MVP: oddiy komandalar asosiy, tugmalar minimal)."""
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


def admin_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Statistika", callback_data="admin:stats")
    builder.button(text="👥 Foydalanuvchi qidirish", callback_data="admin:search_user")
    builder.button(text="🃏 Karta qo'shish", callback_data="admin:add_card")
    builder.button(text="📢 Broadcast", callback_data="admin:broadcast")
    builder.adjust(1)
    return builder.as_markup()


def user_manage_kb(telegram_id: int, is_blocked: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    block_text = "✅ Blokdan chiqarish" if is_blocked else "🚫 Bloklash"
    builder.button(text=block_text, callback_data=f"admin:toggle_block:{telegram_id}")
    builder.button(text="💎 +50 gems", callback_data=f"admin:grant_gems:{telegram_id}:50")
    builder.button(text="💎 +100 gems", callback_data=f"admin:grant_gems:{telegram_id}:100")
    builder.adjust(1)
    return builder.as_markup()
