from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from bot import database as db
from bot.keyboards import RARITY_FILTER_KB

router = Router()

RARITY_EMOJI = {
    "common": "⚪️",
    "rare": "🔵",
    "epic": "🟣",
    "legendary": "🟡",
}

PAGE_SIZE = 10


def format_cards_page(cards, page: int = 0) -> str:
    if not cards:
        return "Sizda hali kartalar yo'q. Kunlik bonus orqali yoki do'kondan gems sotib olib gacha torting."

    start = page * PAGE_SIZE
    chunk = cards[start:start + PAGE_SIZE]

    lines = [f"🃏 Sizning kolleksiyangiz ({len(cards)} ta):\n"]
    for card in chunk:
        emoji = RARITY_EMOJI.get(card["rarity"], "⚪️")
        lines.append(
            f"{emoji} {card['name']} — ATK {card['atk']} / DEF {card['def']}"
        )
    return "\n".join(lines)


@router.message(F.text == "🃏 Kolleksiya")
async def show_collection(message: Message) -> None:
    cards = await db.get_user_cards(message.from_user.id)
    text = format_cards_page(cards)
    await message.answer(text, reply_markup=RARITY_FILTER_KB)


@router.callback_query(F.data.startswith("filter_"))
async def filter_collection(callback: CallbackQuery) -> None:
    rarity = callback.data.replace("filter_", "")
    rarity_filter = None if rarity == "all" else rarity

    cards = await db.get_user_cards(callback.from_user.id, rarity_filter)
    text = format_cards_page(cards)

    await callback.message.edit_text(text, reply_markup=RARITY_FILTER_KB)
    await callback.answer()
