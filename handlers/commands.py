import os
from aiogram import types
from aiogram.types import FSInputFile
from services.order_service import OrderService
from asyncio import to_thread


class CommandHandlers:
    """Телеграм-команди для роботи з замовленнями Budver"""

    def __init__(self, order_service: OrderService):
        self.service = order_service

    async def search(self, message: types.Message):
        # розпізнаємо кількість після команди
        parts = message.text.split()
        limit = 10
        if len(parts) > 1:
            try:
                limit = int(parts[1])
                if limit < 1:
                    limit = 1
                elif limit > 100:
                    limit = 100
            except ValueError:
                limit = 10

        await message.answer(f"🔍 Шукаю {limit} нових замовлень по ремонту в Києві...")

        try:
            orders = await self.service.fetch_and_save_orders_with_limit(limit)

            if not orders:
                await message.answer("❌ Нових замовлень не знайдено.")
                return

            total = len(orders)
            show_limit = min(2, total)
            shown_orders = orders[:show_limit]
            saved_to_db = total - show_limit if total > show_limit else 0

            msg = f"📢 <b>На Budver знайдено {total} нових замовлень!</b>\n"
            msg += "Ось кілька останніх прикладів:\n\n"

            for o in shown_orders:
                msg += (
                    f"🆕 <b>{o['title']}</b>\n"
                    f"🏙️ {o['city']}\n"
                    f"💰 {o['price']}\n"
                    f"📝 {o['desc'][:250]}...\n"
                    f"🔗 <a href='{o['url']}'>Відкрити завдання</a>\n\n"
                )

            if saved_to_db > 0:
                msg += (
                    f"💾 Ще {saved_to_db} замовлень збережено у базу даних.\n"
                    f"📊 Отримати повний список у вигляді Excel-файлу можна командою <b>/export</b>."
                )

            await message.answer(msg, parse_mode="HTML", disable_web_page_preview=True)

        except Exception as e:
            await message.answer(f"⚠️ Помилка: {e}")

        except Exception as e:
            await message.answer(f"⚠️ Помилка: {e}")

    async def export(self, message: types.Message):
        """Формує, надсилає Excel-файл і одразу видаляє його"""
        try:
            path = self.service.export_orders_to_excel()
            doc = FSInputFile(path, filename="orders_export.xlsx")

            await message.answer_document(document=doc, caption="📊 Повний звіт про замовлення Budver")

            if os.path.exists(path):
                os.remove(path)
                print(f"🗑️ Файл {path} видалено після відправлення")

        except Exception as e:
            await message.answer(f"⚠️ Помилка при експорті: {e}")