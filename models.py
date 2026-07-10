"""
SQLAlchemy async modellari.
MVP bosqichida SQLite ishlatiladi, foydalanuvchi ko'payganda
DATABASE_URL o'zgartirilib PostgreSQL'ga o'tish mumkin (kod o'zgarmaydi).
"""
from datetime import datetime
from sqlalchemy import (
    BigInteger, String, Integer, ForeignKey, DateTime, Boolean, func
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str] = mapped_column(String(128), default="")

    gems: Mapped[int] = mapped_column(Integer, default=100)          # premium valyuta
    coins: Mapped[int] = mapped_column(Integer, default=0)           # savdo valyutasi (F3)

    level: Mapped[int] = mapped_column(Integer, default=1)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    losses: Mapped[int] = mapped_column(Integer, default=0)

    last_daily_claim: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    daily_streak: Mapped[int] = mapped_column(Integer, default=0)

    referred_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    referral_count: Mapped[int] = mapped_column(Integer, default=0)

    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_active: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    cards: Mapped[list["UserCard"]] = relationship(back_populates="user")


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    anime: Mapped[str] = mapped_column(String(64))
    rarity: Mapped[str] = mapped_column(String(16))   # common/rare/epic/legendary/mythic
    element: Mapped[str] = mapped_column(String(16), default="neutral")

    atk: Mapped[int] = mapped_column(Integer)
    hp: Mapped[int] = mapped_column(Integer)
    spd: Mapped[int] = mapped_column(Integer)

    ability_name: Mapped[str] = mapped_column(String(64), default="")
    ability_desc: Mapped[str] = mapped_column(String(256), default="")

    image_url: Mapped[str] = mapped_column(String(256), default="")  # R2/local path
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)   # gacha havzasida bormi

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class UserCard(Base):
    """Foydalanuvchining shaxsiy kolleksiyasidagi karta nusxasi."""
    __tablename__ = "user_cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))

    level: Mapped[int] = mapped_column(Integer, default=1)
    obtained_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="cards")
    card: Mapped["Card"] = relationship()


class Transaction(Base):
    """O'chirib bo'lmaydigan audit log — barcha to'lov/gacha/jang harakatlari."""
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(32))       # gacha/purchase/battle_reward/admin_grant
    amount_gems: Mapped[int] = mapped_column(Integer, default=0)
    amount_coins: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str] = mapped_column(String(256), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
