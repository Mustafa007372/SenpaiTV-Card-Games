"""
SQLite bilan ishlash uchun barcha funksiyalar shu yerda.
MVP darajasida SQLite yetarli — rejaning FAZA 2 qismida PostgreSQL'ga
migratsiya qilish ko'zda tutilgan.
"""

import random
from datetime import date, datetime

import aiosqlite

from bot.config import DB_PATH

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    gems INTEGER NOT NULL DEFAULT 0,
    referred_by INTEGER,
    registered_at TEXT NOT NULL,
    last_daily TEXT,
    is_blocked INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS cards (
    card_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    rarity TEXT NOT NULL,
    atk INTEGER NOT NULL,
    def INTEGER NOT NULL,
    image_path TEXT
);

CREATE TABLE IF NOT EXISTS user_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    card_id INTEGER NOT NULL,
    obtained_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (card_id) REFERENCES cards (card_id)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    amount INTEGER NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL
);

-- Rarity bo'yicha tushish ehtimoli (drop rate).
-- Reja hujjatidagi "Iqtisodiy balans" bo'limiga mos: Common 60%, Rare 25%,
-- Epic 12%, Legendary 3%.
"""

RARITY_WEIGHTS = {
    "common": 60,
    "rare": 25,
    "epic": 12,
    "legendary": 3,
}


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(CREATE_TABLES_SQL)
        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        return await cursor.fetchone()


async def create_user(user_id: int, username: str, referred_by: int | None = None) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO users (user_id, username, gems, referred_by, registered_at)
            VALUES (?, ?, 0, ?, ?)
            """,
            (user_id, username, referred_by, datetime.utcnow().isoformat()),
        )
        await db.commit()


async def add_gems(user_id: int, amount: int, reason: str = "") -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET gems = gems + ? WHERE user_id = ?", (amount, user_id)
        )
        await db.execute(
            """
            INSERT INTO transactions (user_id, type, amount, description, created_at)
            VALUES (?, 'credit', ?, ?, ?)
            """,
            (user_id, amount, reason, datetime.utcnow().isoformat()),
        )
        await db.commit()


async def spend_gems(user_id: int, amount: int, reason: str = "") -> bool:
    """
    Gemsni sarflaydi, lekin faqat yetarli mablag' bo'lsa.
    Bir vaqtning o'zida tekshirish va yechish — race condition'dan himoya
    uchun bitta tranzaksiya ichida bajariladi.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT gems FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row is None or row[0] < amount:
            return False

        await db.execute(
            "UPDATE users SET gems = gems - ? WHERE user_id = ?", (amount, user_id)
        )
        await db.execute(
            """
            INSERT INTO transactions (user_id, type, amount, description, created_at)
            VALUES (?, 'debit', ?, ?, ?)
            """,
            (user_id, amount, reason, datetime.utcnow().isoformat()),
        )
        await db.commit()
        return True


async def can_claim_daily(user_id: int) -> bool:
    user = await get_user(user_id)
    if user is None or user["last_daily"] is None:
        return True
    last = date.fromisoformat(user["last_daily"])
    return last < date.today()


async def set_daily_claimed(user_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET last_daily = ? WHERE user_id = ?",
            (date.today().isoformat(), user_id),
        )
        await db.commit()


async def add_card(name: str, rarity: str, atk: int, def_: int, image_path: str = "") -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO cards (name, rarity, atk, def, image_path)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, rarity, atk, def_, image_path),
        )
        await db.commit()
        return cursor.lastrowid


async def get_random_card_by_rarity() -> aiosqlite.Row | None:
    """
    RARITY_WEIGHTS asosida tasodifiy rarity tanlanadi, so'ng shu rarity'dan
    tasodifiy bitta karta qaytariladi. Agar shu rarity'da karta bo'lmasa,
    boshqa mavjud rarity'ga tushadi.
    """
    rarities = list(RARITY_WEIGHTS.keys())
    weights = list(RARITY_WEIGHTS.values())

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        for _ in range(len(rarities)):
            chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]
            cursor = await db.execute(
                "SELECT * FROM cards WHERE rarity = ? ORDER BY RANDOM() LIMIT 1",
                (chosen_rarity,),
            )
            card = await cursor.fetchone()
            if card is not None:
                return card
            # shu rarity bo'sh bo'lsa, ro'yxatdan olib tashlab qayta urinamiz
            idx = rarities.index(chosen_rarity)
            rarities.pop(idx)
            weights.pop(idx)
        return None


async def give_card_to_user(user_id: int, card_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO user_cards (user_id, card_id, obtained_at)
            VALUES (?, ?, ?)
            """,
            (user_id, card_id, datetime.utcnow().isoformat()),
        )
        await db.commit()


async def get_user_cards(user_id: int, rarity_filter: str | None = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if rarity_filter:
            cursor = await db.execute(
                """
                SELECT c.*, uc.obtained_at FROM user_cards uc
                JOIN cards c ON c.card_id = uc.card_id
                WHERE uc.user_id = ? AND c.rarity = ?
                ORDER BY uc.obtained_at DESC
                """,
                (user_id, rarity_filter),
            )
        else:
            cursor = await db.execute(
                """
                SELECT c.*, uc.obtained_at FROM user_cards uc
                JOIN cards c ON c.card_id = uc.card_id
                WHERE uc.user_id = ?
                ORDER BY uc.obtained_at DESC
                """,
                (user_id,),
            )
        return await cursor.fetchall()


async def get_strongest_user_card(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT c.* FROM user_cards uc
            JOIN cards c ON c.card_id = uc.card_id
            WHERE uc.user_id = ?
            ORDER BY (c.atk + c.def) DESC
            LIMIT 1
            """,
            (user_id,),
        )
        return await cursor.fetchone()


async def set_blocked(user_id: int, blocked: bool) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET is_blocked = ? WHERE user_id = ?",
            (1 if blocked else 0, user_id),
        )
        await db.commit()


async def is_blocked(user_id: int) -> bool:
    user = await get_user(user_id)
    return bool(user["is_blocked"]) if user else False
