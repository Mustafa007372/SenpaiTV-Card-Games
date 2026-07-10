"""
Do'kon — Telegram Stars orqali gems sotib olish.

MUHIM (xavfsizlik): har bir to'lov database transaction darajasida
qayta ishlanadi — yarim bajarilgan holat (pul o'tdi, gems berilmadi
yoki aksincha) bo'lishi mumkin emas. successful_payment kelgandan
keyingina gems beriladi va bu bitta commit ichida amalga oshadi.
"""
from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
)

from database.db import async_session
from database import crud
from bot.keyboards.user_kb import shop_packages_kb
from config import config

router = Router(name="shop")


@router.message(F.text == "💎 Do'kon")
async def shop_menu(message: Message):
    await message.answer(
        "💎 <b>Do'kon</b>\n\nTelegram Stars orqali gems sotib oling:",
        reply_markup=shop_packages_kb(config.STARS_PACKAGES),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("buy_gems:"))
async def initiate_purchase(callback: CallbackQuery):
    stars = int(callback.data.split(":")[1])
    gems = config.STARS_PACKAGES.get(stars)
    if not gems:
        await callback.answer("Noto'g'ri paket", show_alert=True)
        return

    await callback.message.answer_invoice(
        title=f"{gems} Gems",
        description=f"{gems} gems hisobingizga qo'shiladi",
        payload=f"gems_{gems}_{callback.from_user.id}",
        currency="XTR",  # Telegram Stars
        prices=[LabeledPrice(label=f"{gems} Gems", amount=stars)],
    )
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    # MVP bosqichida qo'shimcha tekshiruv shart emas — payload formatini tasdiqlaymiz
    if pre_checkout_query.invoice_payload.startswith("gems_"):
        await pre_checkout_query.answer(ok=True)
    else:
        await pre_checkout_query.answer(ok=False, error_message="Noto'g'ri buyurtma")


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    parts = payload.split("_")
    gems = int(parts[1])

    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, message.from_user.id)
        if user:
            await crud.adjust_gems(
                session, user, gems, "purchase",
                f"Stars to'lovi: {message.successful_payment.total_amount} XTR"
            )

    await message.answer(
        f"✅ To'lov muvaffaqiyatli! 💎 +{gems} gems hisobingizga qo'shildi.\n"
        f"Rahmat! 🎉"
    )
