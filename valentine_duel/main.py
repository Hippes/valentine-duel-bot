"""
Main bot application
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.settings import settings
from app.database import init_db
from app.handlers import start, questionnaire, duel
from app.middlewares.db import DbSessionMiddleware


async def main():
    """Main function to start the bot"""
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Initialize database
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")
    
    # Initialize bot and dispatcher
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register middleware
    dp.update.middleware(DbSessionMiddleware())
    
    # Register routers
    dp.include_router(start.router)
    dp.include_router(questionnaire.router)
    dp.include_router(duel.router)
    
    # Start bot
    logger.info("Starting bot...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
