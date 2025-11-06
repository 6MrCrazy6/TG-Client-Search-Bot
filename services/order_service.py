import os
from asyncio import to_thread
from pandas import DataFrame
from database import Database
from parsers.budver_parser import parse_budver_kyiv_repairs
from parsers.rabotniki_parser import parse_rabotniki_search

class OrderService:
    def __init__(self, db: Database):
        self.db = db

    async def fetch_all_sites(self, total_limit: int):
        """Шукає замовлення спочатку на Budver, потім на Rabotniki"""
        half = total_limit // 2
        result = {"budver": [], "rabotniki": []}

        # 🏗 1️⃣ Budver
        print(f"🔹 Парсимо Budver (до {half})...")
        budver_orders = await to_thread(parse_budver_kyiv_repairs, half)
        if budver_orders:
            for o in budver_orders:
                self.db.save_order(o["title"], o["desc"], o["city"], o["price"], o["url"])
            print(f"✅ Budver: знайдено {len(budver_orders)}")
            result["budver"] = budver_orders
        else:
            print("❌ На Budver нових замовлень немає.")

        # 🧱 2️⃣ Rabotniki.ua
        print(f"🔹 Парсимо Rabotniki.ua (до {half})...")
        rabotniki_orders = await to_thread(parse_rabotniki_search, half)
        if rabotniki_orders:
            for o in rabotniki_orders:
                self.db.save_order_rabotniki(o["title"], o["desc"], o["city"], o["price"], o["url"])
            print(f"✅ Rabotniki: знайдено {len(rabotniki_orders)}")
            result["rabotniki"] = rabotniki_orders
        else:
            print("❌ На Rabotniki.ua нових замовлень немає.")

        return result

    def export_orders_to_excel(self, path="orders_export.xlsx"):
        """Экспортирует все заказы из обеих таблиц"""
        try:
            # Убедимся, что путь для сохранения правильный
            if not path:
                path = os.path.join(os.getcwd(), "orders_export.xlsx")  # Используем рабочую директорию

            # Получаем данные из БД
            with self.db.conn.cursor() as cur:
                cur.execute("""
                    SELECT source, title, description, city, price, url FROM (
                        SELECT 'Budver' AS source, title, description, city, price, url, created_at
                        FROM orders_budver
                        UNION ALL
                        SELECT 'Rabotniki.ua', title, description, city, price, url, created_at
                        FROM orders_rabotniki
                    ) AS all_orders
                    ORDER BY source, created_at DESC;
                """)
                rows = cur.fetchall()

            # Преобразуем данные в DataFrame
            df = DataFrame(rows, columns=["Джерело", "Назва", "Опис", "Місто", "Бюджет", "Посилання"])

            # Убедимся, что папка существует
            directory = os.path.dirname(path)
            if not os.path.exists(directory) and directory != '':
                os.makedirs(directory)

            # Сохраняем в Excel
            df.to_excel(path, index=False)
            print(f"Файл успешно создан по пути: {path}")
            return path
        except Exception as e:
            print(f"Ошибка при экспорте: {e}")
            raise