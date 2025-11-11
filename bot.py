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
    dp.message.register(commands.start, F.text == '/start')
    dp.message.register(commands.help, F.text == '/help')
    dp.message.register(commands.search, F.text.startswith('/search'))
    dp.message.register(commands.export, F.text == '/export')
    dp.message.register(commands.clear_all, F.text == '/clear_all')
    dp.message.register(commands.stats, F.text == '/stats')

async def main():
    register_handlers()
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    #db.drop_table("orders_budver")
    #db.drop_table("orders_rabotniki")
    asyncio.run(main())
