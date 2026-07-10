import random

from aiogram import Router, F
from aiogram.types import Message

from bot import database as db
from bot.config import DAILY_BONUS_GEMS

router = Router()

# Botning har jangdagi kuchi tasodifiy oraliqda tanlanadi — bu MVP darajasida
# oddiy, statik formula. Balanslash reja hujjatidagi 6-bandga muvofiq keyingi
# bosqichda simulyatsiya qilinishi kerak.
BOT_ATK_RANGE = (15, 45)
BOT_DEF_RANGE = (15, 45)

BATTLE_WIN_REWARD_GEMS = 15


@router.message(F.text == "⚔️ Jang")
async def start_pve_battle(message: Message) -> None:
    user_id = message.from_user.id
    user = await db.get_user(user_id)

    if user is None:
        await message.answer("Avval /start buyrug'ini bosing.")
        return

    strongest_card = await db.get_strongest_user_card(user_id)
    if strongest_card is None:
        await message.answer(
            "Jangga chiqish uchun kamida bitta kartangiz bo'lishi kerak. "
            "Avval kunlik bonus yoki do'kon orqali karta oling."
        )
        return

    # MUHIM: bu hisoblash to'liq server tomonida bajariladi. Client
    # (foydalanuvchi qurilmasi) hech qanday natijani yubormaydi va
    # yubora olmaydi — bu cheat/firibgarlikning oldini oladi.
    bot_atk = random.randint(*BOT_ATK_RANGE)
    bot_def = random.randint(*BOT_DEF_RANGE)

    user_power = strongest_card["atk"] - bot_def + strongest_card["def"]
    bot_power = bot_atk - strongest_card["def"] + bot_def

    if user_power >= bot_power:
        await db.add_gems(user_id, BATTLE_WIN_REWARD_GEMS, reason="pve_win")
        result_text = (
            f"⚔️ Jang natijasi: G'ALABA!\n\n"
            f"Sizning kartangiz: {strongest_card['name']} "
            f"(ATK {strongest_card['atk']} / DEF {strongest_card['def']})\n"
            f"Raqib bot: ATK {bot_atk} / DEF {bot_def}\n\n"
            f"💎 Mukofot: +{BATTLE_WIN_REWARD_GEMS} gems"
        )
    else:
        result_text = (
            f"⚔️ Jang natijasi: MAG'LUBIYAT\n\n"
            f"Sizning kartangiz: {strongest_card['name']} "
            f"(ATK {strongest_card['atk']} / DEF {strongest_card['def']})\n"
            f"Raqib bot: ATK {bot_atk} / DEF {bot_def}\n\n"
            "Kuchliroq karta to'plab, qayta urinib ko'ring."
        )

    await message.answer(result_text)
