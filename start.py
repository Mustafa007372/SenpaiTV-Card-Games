"""/start komandasi — ro'yxatdan o'tish, referral deep-link ishlov berish."""
from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message

from database.db import async_session
from database import crud
from bot.keyboards.user_kb import main_menu_kb

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    referred_by = None
    if command.args and command.args.startswith("ref_"):
        try:
            referred_by = int(command.args.replace("ref_", ""))
            if referred_by == message.from_user.id:
                referred_by = None  # o'zini-o'zi referral qila olmaydi
        except ValueError:
            referred_by = None

    async with async_session() as session:
        user, created = await crud.get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            referred_by=referred_by,
        )

    if created:
        text = (
            f"🎴 <b>Anime TCG botiga xush kelibsiz, {message.from_user.first_name}!</b>\n\n"
            f"Sizga boshlang'ich bonus sifatida <b>{user.gems} gems</b> berildi.\n\n"
            "🎁 Kunlik bonusni unutmang\n"
            "⚔️ Kartalaringiz bilan jang qiling\n"
            "💎 Do'kondan gems sotib oling va yangi kartalar oching\n\n"
            "Pastdagi menyudan boshlang 👇"
        )
    else:
        text = f"Qaytganingizdan xursandmiz, {message.from_user.first_name}! 👋"

    await message.answer(text, reply_markup=main_menu_kb(), parse_mode="HTML")


@router.message(F.text == "👤 Profil")
async def show_profile(message: Message):
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, message.from_user.id)
        if not user:
            await message.answer("Iltimos, avval /start bosing.")
            return
        collection = await crud.get_user_collection(session, user)

    text = (
        f"👤 <b>{message.from_user.full_name}</b>\n\n"
        f"💎 Gems: {user.gems}\n"
        f"🪙 Coins: {user.coins}\n"
        f"📊 Daraja: {user.level}\n"
        f"🎴 Kartalar soni: {len(collection)}\n"
        f"⚔️ G'alaba/Mag'lubiyat: {user.wins}/{user.losses}\n"
        f"🔥 Kunlik streak: {user.daily_streak}\n"
        f"👥 Referrallar: {user.referral_count}\n"
    )
    await message.answer(text, parse_mode="HTML")
