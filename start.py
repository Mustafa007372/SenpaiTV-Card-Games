from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message

from bot import database as db
from bot.config import REFERRAL_BONUS_GEMS
from bot.keyboards import MAIN_MENU

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject) -> None:
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    existing_user = await db.get_user(user_id)

    if existing_user is not None:
        await message.answer(
            f"Xush kelibsiz qaytganingiz bilan, {username}!", reply_markup=MAIN_MENU
        )
        return

    referred_by = None
    if command.args and command.args.isdigit():
        potential_referrer_id = int(command.args)
        # O'zini o'zi referral qilishning oldini olish
        if potential_referrer_id != user_id:
            referrer = await db.get_user(potential_referrer_id)
            if referrer is not None:
                referred_by = potential_referrer_id

    await db.create_user(user_id, username, referred_by)

    welcome_text = (
        f"Salom, {username}! Karta-kolleksiya botiga xush kelibsiz.\n\n"
        "🎁 Har kuni bepul gacha tortish imkoniyatiga ega bo'lasiz.\n"
        "🃏 Kartalar to'plang, jangda kuchingizni sinang.\n\n"
        "Boshlash uchun quyidagi menyudan foydalaning."
    )
    await message.answer(welcome_text, reply_markup=MAIN_MENU)

    # Referral bonusi — faqat user birinchi marta ro'yxatdan o'tganda,
    # ikkala tomonga ham beriladi. Fraud oldini olish uchun bonus faqat
    # shu yerda, bir marta beriladi (keyingi /start chaqiruvlarida emas).
    if referred_by is not None:
        await db.add_gems(referred_by, REFERRAL_BONUS_GEMS, reason="referral_bonus")
        await db.add_gems(user_id, REFERRAL_BONUS_GEMS, reason="referral_welcome_bonus")
        try:
            await message.bot.send_message(
                referred_by,
                f"🎉 Sizning referral havolangiz orqali yangi user qo'shildi! "
                f"+{REFERRAL_BONUS_GEMS} gems oldingiz.",
            )
        except Exception:
            # Referrer botni bloklagan bo'lishi mumkin — bu xato botni
            # to'xtatmasligi kerak
            pass


@router.message(F.text == "👤 Profil")
async def show_profile(message: Message) -> None:
    user = await db.get_user(message.from_user.id)
    if user is None:
        await message.answer("Avval /start buyrug'ini bosing.")
        return

    cards = await db.get_user_cards(message.from_user.id)
    text = (
        f"👤 Profil\n\n"
        f"💎 Gems: {user['gems']}\n"
        f"🃏 Kartalar soni: {len(cards)}\n"
        f"📅 Ro'yxatdan o'tgan sana: {user['registered_at'][:10]}"
    )
    await message.answer(text)
