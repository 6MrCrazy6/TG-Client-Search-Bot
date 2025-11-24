import os
from aiogram import types
from aiogram.types import FSInputFile
from services.order_service import OrderService


class CommandHandlers:
    """Телеграм-команди для роботи з замовленнями Kabanchik + Budver + Rabotniki"""

    def __init__(self, order_service: OrderService):
        self.service = order_service

    # ─────────────────────────────
    # 🏁 /start — Привітання
    # ─────────────────────────────
    async def start(self, message: types.Message):
        text = (
            "👋 <b>Вітаю у Search Client!</b>\n\n"
            "Цей бот автоматично шукає нові замовлення у сфері ремонту з трьох сайтів:\n"
            "🐗 Kabanchik.ua\n"
            "🏗 Budver.ua\n"
            "🧱 Rabotniki.ua\n\n"
            "Використовуйте команду <b>/help</b>, щоб побачити повний список можливостей."
        )
        await message.answer(text, parse_mode="HTML")

    # ─────────────────────────────
    # ℹ️ /help — Список команд
    # ─────────────────────────────
    async def help(self, message: types.Message):
        text = (
            "🛠 <b>Доступні команди:</b>\n\n"
            "🔍 <b>/search [кількість]</b> — знайти нові замовлення (наприклад, /search 15)\n"
            "📊 <b>/export</b> — експортувати всі знайдені замовлення у Excel-файл\n"
            "🧹 <b>/clear_all</b> — очистити усі таблиці з бази даних\n"
            "📈 <b>/stats</b> — статистика кількості замовлень у базі\n"
            "ℹ️ <b>/help</b> — показати список команд\n"
            "🏁 <b>/start</b> — привітальне повідомлення"
        )
        await message.answer(text, parse_mode="HTML")

    # ─────────────────────────────
    # 🔍 /search — Пошук нових замовлень
    # ─────────────────────────────
    async def search(self, message: types.Message):
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
            results = await self.service.fetch_all_sites(limit)

            kabanchik_orders = results.get("kabanchik", [])
            budver_orders = results.get("budver", [])
            rabotniki_orders = results.get("rabotniki", [])

            total_found = len(kabanchik_orders) + len(budver_orders) + len(rabotniki_orders)
            msg = f"📢 <b>Знайдено {total_found} нових замовлень!</b>\n\n"

            # 🐗 Kabanchik.ua
            msg += f"🐗 <b>Kabanchik.ua:</b> {len(kabanchik_orders)} знайдено.\n"
            if kabanchik_orders:
                show_k = min(2, len(kabanchik_orders))
                for o in kabanchik_orders[:show_k]:
                    msg += (
                        f"🆕 <b>{o['title']}</b>\n"
                        f"🏙️ {o['city']}\n"
                        f"💰 {o['price']}\n"
                        f"🔗 <a href='{o['url']}'>Відкрити завдання</a>\n\n"
                    )
                if len(kabanchik_orders) > show_k:
                    msg += f"💾 Ще {len(kabanchik_orders) - show_k} додано у базу.\n\n"
            else:
                msg += "❌ Нових немає.\n\n"

            # 🏗 Budver
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

            # 🧱 Rabotniki.ua
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

    # ─────────────────────────────
    # 📊 /export — Експорт у Excel
    # ─────────────────────────────
    async def export(self, message: types.Message):
        try:
            path = self.service.export_orders_to_excel()
            doc = FSInputFile(path, filename="orders_export.xlsx")
            await message.answer_document(document=doc, caption="📊 Повний звіт про замовлення")

            if os.path.exists(path):
                os.remove(path)
                print(f"🗑️ Файл {path} видалено після відправки")

        except Exception as e:
            await message.answer(f"⚠️ Помилка при експорті: {e}")

    # ─────────────────────────────
    # 🧹 /clear_all — Очистка таблиць
    # ─────────────────────────────
    async def clear_all(self, message: types.Message):
        try:
            db = self.service.db
            db.drop_table("orders_kabanchik")
            db.drop_table("orders_budver")
            db.drop_table("orders_rabotniki")
            await message.answer("🧹 Усі таблиці замовлень очищено!")
        except Exception as e:
            await message.answer(f"⚠️ Помилка при очищенні: {e}")

    # ─────────────────────────────
    # 📈 /stats — Статистика бази
    # ─────────────────────────────
    async def stats(self, message: types.Message):
        try:
            db = self.service.db
            with db.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM orders_kabanchik;")
                kabanchik = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM orders_budver;")
                budver = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM orders_rabotniki;")
                rabotniki = cur.fetchone()[0]

            total = kabanchik + budver + rabotniki
            msg = (
                "📈 <b>Статистика бази:</b>\n\n"
                f"🐗 Kabanchik.ua — <b>{kabanchik}</b>\n"
                f"🏗 Budver — <b>{budver}</b>\n"
                f"🧱 Rabotniki.ua — <b>{rabotniki}</b>\n"
                f"────────────────────\n"
                f"💾 Всього записів: <b>{total}</b>"
            )
            await message.answer(msg, parse_mode="HTML")

        except Exception as e:
            await message.answer(f"⚠️ Помилка при отриманні статистики: {e}")
