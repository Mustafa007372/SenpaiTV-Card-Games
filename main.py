"""
Bot ishga tushirish nuqtasi.
Ishga tushirish: python main.py
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from database.db import init_db

from bot.middlewares.throttling import ThrottlingMiddleware, BlockedUserMiddleware

from bot.handlers.user import start, daily, cards, battle, shop, support
from bot.handlers.admin import admin


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    if not config.BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN topilmadi! .env faylida BOT_TOKEN=... ni to'ldiring "
            "(.env.example faylga qarang)."
        )

    await init_db()
    logger.info("Database tayyor.")

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Middlewarelar — barcha update turlari uchun
    dp.update.middleware(ThrottlingMiddleware())
    dp.update.middleware(BlockedUserMiddleware())

    # Routerlar — admin birinchi bo'lishi shart emas, lekin aniqlik uchun
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(daily.router)
    dp.include_router(cards.router)
    dp.include_router(battle.router)
    dp.include_router(shop.router)
    dp.include_router(support.router)

    logger.info("Bot ishga tushdi.")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi.")
