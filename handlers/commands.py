import os
from aiogram import types
from aiogram.types import FSInputFile
from services.order_service import OrderService


class CommandHandlers:
    """Телеграм-команди для роботи з замовленнями Budver + Rabotniki"""

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
            # 🔹 Отримуємо з двох сайтів одразу
            results = await self.service.fetch_all_sites(limit)

            budver_orders = results["budver"]
            rabotniki_orders = results["rabotniki"]

            total_found = len(budver_orders) + len(rabotniki_orders)
            msg = f"📢 <b>Знайдено {total_found} нових замовлень!</b>\n\n"

            # ======= 🏗 Budver =======
            msg += f"🏗 <b>Budver:</b> {len(budver_orders)} знайдено.\n"
            if budver_orders:
                show_b = min(2, len(budver_orders))
                for o in budver_orders[:show_b]:
                    msg += (
                        f"🆕 <b>{o['title']}</b>\n"
                        f"🏙️ {o['city']}\n"
                        f"💰 {o['price']}\n"
                        f"📝 {o['desc'][:200]}...\n"
                        f"🔗 <a href='{o['url']}'>Відкрити завдання</a>\n\n"
                    )
                if len(budver_orders) > show_b:
                    msg += f"💾 Ще {len(budver_orders) - show_b} додано у базу.\n\n"
            else:
                msg += "❌ Нових немає.\n\n"

            # ======= 🧱 Rabotniki =======
            msg += f"🧱 <b>Rabotniki.ua:</b> {len(rabotniki_orders)} знайдено.\n"
            if rabotniki_orders:
                show_r = min(2, len(rabotniki_orders))
                for o in rabotniki_orders[:show_r]:
                    msg += (
                        f"🆕 <b>{o['title']}</b>\n"
                        f"🏙️ {o['city']}\n"
                        f"💰 {o['price']}\n"
                        f"📝 {o['desc'][:200]}...\n"
                        f"🔗 <a href='{o['url']}'>Відкрити завдання</a>\n\n"
                    )
                if len(rabotniki_orders) > show_r:
                    msg += f"💾 Ще {len(rabotniki_orders) - show_r} додано у базу.\n\n"
            else:
                msg += "❌ Нових немає.\n\n"

            msg += "📊 Отримати повний список у вигляді Excel-файлу — команда <b>/export</b>."
            await message.answer(msg, parse_mode="HTML", disable_web_page_preview=True)

        except Exception as e:
            await message.answer(f"⚠️ Помилка: {e}")

    async def export(self, message: types.Message):
        """Формирует, отправляет Excel-файл и сразу удаляет его после отправки"""
        try:
            # Генерация файла
            path = self.service.export_orders_to_excel()

            # Открываем файл для отправки
            doc = FSInputFile(path, filename="orders_export.xlsx")

            # Отправляем файл
            await message.answer_document(document=doc, caption="📊 Повний звіт про замовлення")

            # После отправки удаляем файл
            if os.path.exists(path):
                os.remove(path)
                print(f"🗑️ Файл {path} удалён после отправки")

        except Exception as e:
            await message.answer(f"⚠️ Ошибка при экспорте: {e}")