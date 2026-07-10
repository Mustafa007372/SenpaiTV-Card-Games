from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot import database as db
from bot.config import ADMIN_IDS

router = Router()

VALID_RARITIES = {"common", "rare", "epic", "legendary"}


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("addcard"))
async def add_card_command(message: Message) -> None:
    """
    Format: /addcard Nomi | rarity | atk | def
    Masalan: /addcard Ajdaho | epic | 80 | 60
    """
    if not is_admin(message.from_user.id):
        return

    args_text = message.text.replace("/addcard", "", 1).strip()
    parts = [p.strip() for p in args_text.split("|")]

    if len(parts) != 4:
        await message.answer(
            "Noto'g'ri format. Foydalanish:\n"
            "/addcard Nomi | rarity | atk | def\n"
            "Masalan: /addcard Ajdaho | epic | 80 | 60"
        )
        return

    name, rarity, atk_str, def_str = parts
    rarity = rarity.lower()

    if rarity not in VALID_RARITIES:
        await message.answer(
            f"Noto'g'ri rarity. Ruxsat etilganlar: {', '.join(VALID_RARITIES)}"
        )
        return

    if not (atk_str.isdigit() and def_str.isdigit()):
        await message.answer("ATK va DEF butun son bo'lishi kerak.")
        return

    card_id = await db.add_card(name, rarity, int(atk_str), int(def_str))
    await message.answer(
        f"✅ Karta qo'shildi: {name} (ID: {card_id}, {rarity}, "
        f"ATK {atk_str} / DEF {def_str})"
    )


@router.message(Command("block"))
async def block_user_command(message: Message) -> None:
    """Format: /block <user_id>"""
    if not is_admin(message.from_user.id):
        return

    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Foydalanish: /block <user_id>")
        return

    target_id = int(args[1])
    await db.set_blocked(target_id, True)
    await message.answer(f"🚫 User {target_id} bloklandi.")


@router.message(Command("unblock"))
async def unblock_user_command(message: Message) -> None:
    """Format: /unblock <user_id>"""
    if not is_admin(message.from_user.id):
        return

    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Foydalanish: /unblock <user_id>")
        return

    target_id = int(args[1])
    await db.set_blocked(target_id, False)
    await message.answer(f"✅ User {target_id} blokdan chiqarildi.")


@router.message(Command("stats"))
async def stats_command(message: Message) -> None:
    """MVP darajasidagi minimal statistika. To'liq dashboard FAZA 2'da."""
    if not is_admin(message.from_user.id):
        return

    import aiosqlite
    from bot.config import DB_PATH

    async with aiosqlite.connect(DB_PATH) as db_conn:
        cursor = await db_conn.execute("SELECT COUNT(*) FROM users")
        total_users = (await cursor.fetchone())[0]

        cursor = await db_conn.execute(
            "SELECT COUNT(*) FROM users WHERE is_blocked = 1"
        )
        blocked_users = (await cursor.fetchone())[0]

        cursor = await db_conn.execute("SELECT COUNT(*) FROM cards")
        total_cards = (await cursor.fetchone())[0]

        cursor = await db_conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM transactions "
            "WHERE type = 'debit' AND description = 'shop_purchase'"
        )
        # Eslatma: bu gems sarfini ko'rsatadi, real pul daromadi emas.
        # Real Stars daromadini hisoblash uchun successful_payment
        # loglarini alohida jadvalga yozish tavsiya etiladi (FAZA 2).

    await message.answer(
        f"📊 Statistika\n\n"
        f"Jami foydalanuvchilar: {total_users}\n"
        f"Bloklangan: {blocked_users}\n"
        f"Jami kartalar turi: {total_cards}"
    )
