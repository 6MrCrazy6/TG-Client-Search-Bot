from aiogram import types
from services.order_service import OrderService


class CommandHandlers:
    """Класс Telegram-команд, зависящий от бизнес-логики, а не от деталей"""

    def __init__(self, order_service: OrderService):
        self.service = order_service

    async def search(self, message: types.Message):
        await message.answer("🔍 Шукаю нові замовлення по ремонту в Києві...")

        try:
            # ✅ вызываем асинхронно
            orders = await self.service.fetch_and_save_orders()

            if not orders:
                await message.answer("❌ Нових замовлень не знайдено.")
                return

            for o in orders[:10]:
                msg = (
                    f"🆕 <b>{o['title']}</b>\n"
                    f"{o['desc']}\n\n"
                    f"🏙️ {o['city'] or '-'} | 💰 {o['price'] or '-'}\n"
                    f"🔗 {o['url']}"
                )
                await message.answer(msg, parse_mode="HTML")

        except Exception as e:
            await message.answer(f"⚠️ Помилка: {e}")
