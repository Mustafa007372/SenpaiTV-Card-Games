"""
Foydalanuvchi-admin aloqa. Foydalanuvchi xabar yozadi,
avtomatik barcha adminlarga forward qilinadi.
"""
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.user_kb import support_category_kb
from config import config

router = Router(name="support")

CATEGORY_LABELS = {
    "payment": "💳 To'lov muammosi",
    "bug": "🐞 Bug xatolik",
    "suggestion": "💡 Taklif",
    "other": "❓ Boshqa",
}


class SupportStates(StatesGroup):
    waiting_message = State()


@router.message(F.text == "☎️ Yordam")
async def support_menu(message: Message):
    await message.answer(
        "☎️ Qanday yordam kerak? Muammo turini tanlang:",
        reply_markup=support_category_kb(),
    )


@router.callback_query(F.data.startswith("support_cat:"))
async def choose_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split(":")[1]
    await state.update_data(category=category)
    await state.set_state(SupportStates.waiting_message)
    await callback.message.answer(
        f"{CATEGORY_LABELS[category]}\n\nEndi muammoingizni batafsil yozing:"
    )
    await callback.answer()


@router.message(SupportStates.waiting_message)
async def receive_support_message(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    category = data.get("category", "other")

    admin_text = (
        f"📨 <b>Yangi murojaat</b>\n"
        f"Toifa: {CATEGORY_LABELS.get(category, category)}\n"
        f"Foydalanuvchi: @{message.from_user.username or '—'} (ID: {message.from_user.id})\n\n"
        f"Xabar:\n{message.text}\n\n"
        f"Javob berish uchun: <code>/reply {message.from_user.id} matningiz</code>"
    )

    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text, parse_mode="HTML")
        except Exception:
            pass  # admin botni bloklagan bo'lishi mumkin — davom etaveramiz

    await message.answer("✅ Murojaatingiz qabul qilindi. Tez orada javob beramiz.")
    await state.clear()
