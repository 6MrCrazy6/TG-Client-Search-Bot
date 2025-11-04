import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from config import Config
from database import Database
from services.order_service import OrderService
from handlers.commands import CommandHandlers

logging.basicConfig(level=logging.INFO)

cfg = Config()
bot = Bot(token=cfg.BOT_TOKEN)
dp = Dispatcher()

# зависимости
db = Database(cfg)
service = OrderService(db)
commands = CommandHandlers(service)


def register_handlers():
    dp.message.register(commands.search, F.text == '/search')


async def main():
    register_handlers()
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
