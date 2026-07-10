from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    LabeledPrice,
    PreCheckoutQuery,
)

from bot import database as db
from bot.keyboards import shop_keyboard

router = Router()

# gems miqdori -> (Stars narxi, ko'rsatiladigan nom)
# Telegram Stars uchun currency har doim "XTR" bo'ladi, provider_token
# kerak emas (Stars — Telegram'ning o'z ichki valyutasi).
SHOP_ITEMS = {
    "buy_100": (100, 50, "100 Gems"),
    "buy_550": (550, 250, "550 Gems"),
    "buy_1200": (1200, 500, "1200 Gems"),
}


@router.message(F.text == "🛒 Do'kon")
async def show_shop(message: Message) -> None:
    await message.answer(
        "🛒 Do'kon\n\nGems sotib olish uchun variantni tanlang:",
        reply_markup=shop_keyboard(),
    )


@router.callback_query(F.data.startswith("buy_"))
async def send_invoice_for_gems(callback: CallbackQuery) -> None:
    item = SHOP_ITEMS.get(callback.data)
    if item is None:
        await callback.answer("Noma'lum mahsulot.", show_alert=True)
        return

    gems_amount, stars_price, title = item

    await callback.message.answer_invoice(
        title=title,
        description=f"{gems_amount} ta gems hisobingizga qo'shiladi.",
        payload=f"gems_{gems_amount}_{callback.from_user.id}",
        currency="XTR",
        prices=[LabeledPrice(label=title, amount=stars_price)],
    )
    await callback.answer()


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery) -> None:
    # Bu yerda to'lovdan oldingi so'nggi tekshiruv bajariladi (masalan,
    # user bloklanganmi). Har doim tasdiqlash kerak, aks holda to'lov
    # bekor bo'ladi.
    user = await db.get_user(pre_checkout_query.from_user.id)
    if user is not None and user["is_blocked"]:
        await pre_checkout_query.answer(
            ok=False, error_message="Akkountingiz bloklangan, to'lov qabul qilinmaydi."
        )
        return
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message) -> None:
    payload = message.successful_payment.invoice_payload
    # payload format: gems_<amount>_<user_id>
    try:
        parts = payload.split("_")
        gems_amount = int(parts[1])
    except (IndexError, ValueError):
        await message.answer(
            "To'lov qabul qilindi, lekin buyurtmani qayta ishlashda xato yuz berdi. "
            "Iltimos, admin bilan bog'laning."
        )
        return

    await db.add_gems(message.from_user.id, gems_amount, reason="shop_purchase")
    await message.answer(
        f"✅ To'lov muvaffaqiyatli! +{gems_amount} gems hisobingizga qo'shildi."
    )
