import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import BOT_TOKEN, ADMIN_IDS
from bot.database import init_db
from bot.handlers import start, daily, collection, pve, shop, admin

# Xato loglari — MVP darajasida oddiy fayl + konsolga yoziladi.
# Reja hujjatidagi "monitoring" talabiga muvofiq: xatolar ko'rinadigan
# joyda saqlanishi kerak.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot_errors.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


async def notify_admins_on_startup(bot: Bot) -> None:
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, "✅ Bot ishga tushdi.")
        except Exception:
            # Admin botni bloklagan yoki hali /start bosmagan bo'lishi mumkin
            logger.warning("Admin %s ga xabar yuborib bo'lmadi.", admin_id)


async def main() -> None:
    await init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(daily.router)
    dp.include_router(collection.router)
    dp.include_router(pve.router)
    dp.include_router(shop.router)
    dp.include_router(admin.router)

    await notify_admins_on_startup(bot)

    try:
        await dp.start_polling(bot)
    except Exception:
        logger.exception("Bot to'xtadi kutilmagan xato tufayli:")
        raise


if __name__ == "__main__":
    asyncio.run(main())
