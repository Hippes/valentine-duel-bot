"""
Database session middleware
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.database import async_session_maker


class DbSessionMiddleware(BaseMiddleware):
    """Middleware to provide database session to handlers"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with async_session_maker() as session:
            data["session"] = session
            return await handler(event, data)
