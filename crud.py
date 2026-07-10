"""
Barcha database so'rovlari shu yerda — handlerlar to'g'ridan-to'g'ri
SQL/ORM bilan ishlamaydi, faqat shu funksiyalarni chaqiradi.
"""
from datetime import datetime, timedelta
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Card, UserCard, Transaction
from config import config


# ---------- USER ----------

async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    full_name: str,
    referred_by: int | None = None,
) -> tuple[User, bool]:
    """Foydalanuvchini qaytaradi, agar mavjud bo'lmasa yaratadi.
    Qaytaradi: (user, created_yangi_bo'lsa_True)
    """
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user:
        user.last_active = datetime.utcnow()
        if username:
            user.username = username
        await session.commit()
        return user, False

    is_admin = telegram_id in config.ADMIN_IDS
    user = User(
        telegram_id=telegram_id,
        username=username,
        full_name=full_name,
        gems=config.STARTING_GEMS,
        is_admin=is_admin,
        referred_by=referred_by,
    )
    session.add(user)
    await session.flush()

    # Referral bonusi — kunlik limit bilan
    if referred_by:
        await _apply_referral_bonus(session, referred_by)

    await session.commit()
    return user, True


async def _apply_referral_bonus(session: AsyncSession, referrer_telegram_id: int):
    result = await session.execute(select(User).where(User.telegram_id == referrer_telegram_id))
    referrer = result.scalar_one_or_none()
    if not referrer:
        return

    # Kunlik limitni tekshirish (oddiy yondashuv: referral_count bugungi kun uchun
    # alohida hisoblanmaydi bu MVP'da — F2'da kunlik jadval qo'shiladi)
    if referrer.referral_count >= config.REFERRAL_DAILY_LIMIT * 1000:
        return  # umumiy cheksiz limit, kunlik limit F2'da to'liq amalga oshiriladi

    referrer.gems += config.REFERRAL_BONUS_GEMS
    referrer.referral_count += 1
    session.add(Transaction(
        user_id=referrer.id,
        type="referral_bonus",
        amount_gems=config.REFERRAL_BONUS_GEMS,
        description="Referral orqali yangi foydalanuvchi taklif qilindi",
    ))


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def adjust_gems(session: AsyncSession, user: User, amount: int, tx_type: str, description: str = "") -> bool:
    """Gems balansini o'zgartiradi. Manfiy bo'lsa va yetarli mablag' bo'lmasa False qaytaradi.
    Bu funksiya ATOMIK — bitta commit ichida balans + audit log birga yoziladi.
    """
    if amount < 0 and user.gems + amount < 0:
        return False
    user.gems += amount
    session.add(Transaction(
        user_id=user.id,
        type=tx_type,
        amount_gems=amount,
        description=description,
    ))
    await session.commit()
    return True


# ---------- CARDS ----------

async def get_active_cards_by_rarity(session: AsyncSession, rarity: str) -> list[Card]:
    result = await session.execute(
        select(Card).where(Card.rarity == rarity, Card.is_active == True)  # noqa: E712
    )
    return list(result.scalars().all())


async def get_card(session: AsyncSession, card_id: int) -> Card | None:
    result = await session.execute(select(Card).where(Card.id == card_id))
    return result.scalar_one_or_none()


async def add_card_to_user(session: AsyncSession, user: User, card: Card) -> UserCard:
    user_card = UserCard(user_id=user.id, card_id=card.id)
    session.add(user_card)
    await session.commit()
    await session.refresh(user_card)
    return user_card


async def get_user_collection(
    session: AsyncSession, user: User, rarity: str | None = None
) -> list[UserCard]:
    query = select(UserCard).where(UserCard.user_id == user.id)
    result = await session.execute(query)
    items = list(result.scalars().all())
    # rarity bo'yicha filtrlash (kartani birga yuklab)
    filtered = []
    for uc in items:
        card = await get_card(session, uc.card_id)
        uc.card = card
        if rarity is None or (card and card.rarity == rarity):
            filtered.append(uc)
    return filtered


async def create_card(session: AsyncSession, **kwargs) -> Card:
    card = Card(**kwargs)
    session.add(card)
    await session.commit()
    await session.refresh(card)
    return card


# ---------- DAILY ----------

async def can_claim_daily(user: User) -> bool:
    if user.last_daily_claim is None:
        return True
    elapsed = datetime.utcnow() - user.last_daily_claim
    return elapsed >= timedelta(hours=config.DAILY_GACHA_COOLDOWN_HOURS)


async def claim_daily(session: AsyncSession, user: User) -> int:
    """Kunlik bonusni beradi, streak'ni yangilaydi. Qaytaradi: berilgan gems miqdori."""
    now = datetime.utcnow()
    if user.last_daily_claim and (now - user.last_daily_claim) < timedelta(hours=48):
        user.daily_streak += 1
    else:
        user.daily_streak = 1

    bonus = 20 + min(user.daily_streak * 5, 100)  # streak qancha uzun bo'lsa shuncha ko'p
    user.gems += bonus
    user.last_daily_claim = now
    session.add(Transaction(
        user_id=user.id, type="daily_bonus", amount_gems=bonus,
        description=f"Kunlik bonus, streak={user.daily_streak}",
    ))
    await session.commit()
    return bonus


# ---------- STATS (admin) ----------

async def get_total_users(session: AsyncSession) -> int:
    result = await session.execute(select(func.count(User.id)))
    return result.scalar_one()


async def get_active_users_since(session: AsyncSession, hours: int = 24) -> int:
    since = datetime.utcnow() - timedelta(hours=hours)
    result = await session.execute(select(func.count(User.id)).where(User.last_active >= since))
    return result.scalar_one()


async def search_user(session: AsyncSession, query: str) -> User | None:
    """Username yoki telegram_id bo'yicha qidiradi."""
    if query.isdigit():
        return await get_user_by_telegram_id(session, int(query))
    result = await session.execute(select(User).where(User.username == query.lstrip("@")))
    return result.scalar_one_or_none()


async def get_all_user_telegram_ids(session: AsyncSession) -> list[int]:
    result = await session.execute(select(User.telegram_id).where(User.is_blocked == False))  # noqa: E712
    return [row[0] for row in result.all()]
