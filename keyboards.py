from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎁 Kunlik bonus"), KeyboardButton(text="🃏 Kolleksiya")],
        [KeyboardButton(text="⚔️ Jang"), KeyboardButton(text="🛒 Do'kon")],
        [KeyboardButton(text="👤 Profil")],
    ],
    resize_keyboard=True,
)

RARITY_FILTER_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Hammasi", callback_data="filter_all"),
            InlineKeyboardButton(text="Common", callback_data="filter_common"),
        ],
        [
            InlineKeyboardButton(text="Rare", callback_data="filter_rare"),
            InlineKeyboardButton(text="Epic", callback_data="filter_epic"),
        ],
        [InlineKeyboardButton(text="Legendary", callback_data="filter_legendary")],
    ]
)


def shop_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="100 Gems — ⭐️ 50 Stars", callback_data="buy_100")],
            [InlineKeyboardButton(text="550 Gems — ⭐️ 250 Stars", callback_data="buy_550")],
            [InlineKeyboardButton(text="1200 Gems — ⭐️ 500 Stars", callback_data="buy_1200")],
        ]
    )
