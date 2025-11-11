import os
from asyncio import to_thread
from pandas import DataFrame
from database import Database
from parsers.kabanchik_parser import login_kabanchik, parse_kabanchik_orders
from parsers.rabotniki_parser import parse_rabotniki_search
from parsers.budver_parser import parse_budver_kyiv_repairs


class OrderService:
    """Сервіс для збору замовлень з усіх сайтів"""

    def __init__(self, db: Database):
        self.db = db

    # ─────────────────────────────────────────────────────────────
    # 🔍 Основний метод пошуку — Kabanchik + Budver + Rabotniki
    # ─────────────────────────────────────────────────────────────
    async def fetch_all_sites(self, total_limit: int):
        """Шукає замовлення з усіх трьох сайтів (Kabanchik, Budver, Rabotniki)"""
        part = max(1, total_limit // 3)
        result = {"kabanchik": [], "budver": [], "rabotniki": []}

        # 🐗 Kabanchik.ua
        try:
            print(f"🔹 Парсимо Kabanchik.ua (до {part})...")
            from config import Config
            cfg = Config()
            driver = await to_thread(login_kabanchik, cfg.KABANCHIK_LOGIN, cfg.KABANCHIK_PASSWORD)
            kabanchik_orders = await to_thread(parse_kabanchik_orders, driver, part)
            if driver:
                driver.quit()

            if kabanchik_orders:
                for o in kabanchik_orders:
                    self.db.save_order(
                        title=o.get("title", "—"),
                        description="—",
                        city=o.get("city", "Київ"),
                        price=o.get("price", "—"),
                        url=o.get("url"),
                        source="kabanchik"
                    )
                result["kabanchik"] = kabanchik_orders
                print(f"✅ Kabanchik: знайдено {len(kabanchik_orders)}")
            else:
                print("❌ Kabanchik: нових замовлень немає.")
        except Exception as e:
            print(f"⚠️ Помилка Kabanchik: {e}")

        # 🏗 Budver
        try:
            print(f"🔹 Парсимо Budver (до {part})...")
            budver_orders = await to_thread(parse_budver_kyiv_repairs, part)
            if budver_orders:
                for o in budver_orders:
                    self.db.save_order(
                        o["title"], o["desc"], o["city"], o["price"], o["url"], source="budver"
                    )
                result["budver"] = budver_orders
                print(f"✅ Budver: знайдено {len(budver_orders)}")
            else:
                print("❌ Budver: нових замовлень немає.")
        except Exception as e:
            print(f"⚠️ Помилка Budver: {e}")

        # 🧱 Rabotniki.ua
        try:
            print(f"🔹 Парсимо Rabotniki.ua (до {part})...")
            rabotniki_orders = await to_thread(parse_rabotniki_search, part)
            if rabotniki_orders:
                for o in rabotniki_orders:
                    self.db.save_order_rabotniki(
                        o["title"], o["desc"], o["city"], o["price"], o["url"]
                    )
                result["rabotniki"] = rabotniki_orders
                print(f"✅ Rabotniki: знайдено {len(rabotniki_orders)}")
            else:
                print("❌ Rabotniki.ua: нових замовлень немає.")
        except Exception as e:
            print(f"⚠️ Помилка Rabotniki.ua: {e}")

        return result

    # ─────────────────────────────────────────────────────────────
    # 📊 Експорт у Excel
    # ─────────────────────────────────────────────────────────────
    def export_orders_to_excel(self, path="orders_export.xlsx"):
        """Експортує всі замовлення з трьох джерел у Excel"""
        try:
            if not path:
                path = os.path.join(os.getcwd(), "orders_export.xlsx")

            with self.db.conn.cursor() as cur:
                cur.execute("""
                    SELECT source, title, description, city, price, url FROM (
                        SELECT 'Kabanchik' AS source, title, description, city, price, url, created_at
                        FROM orders_kabanchik
                        UNION ALL
                        SELECT 'Budver', title, description, city, price, url, created_at
                        FROM orders_budver
                        UNION ALL
                        SELECT 'Rabotniki.ua', title, description, city, price, url, created_at
                        FROM orders_rabotniki
                    ) AS all_orders
                    ORDER BY source, created_at DESC;
                """)
                rows = cur.fetchall()

            df = DataFrame(rows, columns=["Джерело", "Назва", "Опис", "Місто", "Бюджет", "Посилання"])
            df.to_excel(path, index=False)
            print(f"📁 Файл успішно створено: {path}")
            return path
        except Exception as e:
            print(f"❌ Помилка експорту: {e}")
            raise
