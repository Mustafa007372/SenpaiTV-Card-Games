"""
Rate limiting middleware — bitta foydalanuvchi soniyasiga
belgilangan sondan ko'p so'rov yubora olmaydi (spam/abuse oldini olish).
"""
import time
from typing import Callable, Awaitable, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from config import config


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self):
        self._last_call: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user:
            now = time.monotonic()
            last = self._last_call.get(user.id, 0)
            if now - last < config.THROTTLE_RATE_LIMIT:
                return  # so'rov e'tiborsiz qoldiriladi (javob yuborilmaydi)
            self._last_call[user.id] = now
        return await handler(event, data)


class BlockedUserMiddleware(BaseMiddleware):
    """Bloklangan foydalanuvchilarning so'rovlarini rad etadi."""

    async def __call__(self, handler, event: Update, data: dict[str, Any]) -> Any:
        from database.db import async_session
        from database import crud

        user = data.get("event_from_user")
        if user:
            async with async_session() as session:
                db_user = await crud.get_user_by_telegram_id(session, user.id)
                if db_user and db_user.is_blocked:
                    return  # javob yo'q
        return await handler(event, data)
