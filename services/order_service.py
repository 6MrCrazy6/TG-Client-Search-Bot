from database import Database
from asyncio import to_thread
from parsers.budver_parser import parse_budver_kyiv_repairs

class OrderService:
    def __init__(self, db: Database):
        self.db = db

    async def fetch_and_save_orders_with_limit(self, limit: int):
        """Парсить вказану кількість замовлень Budver"""
        orders = await to_thread(parse_budver_kyiv_repairs, limit)
        for o in orders:
            self.db.save_order(o["title"], o["desc"], o["city"], o["price"], o["url"])
        return orders

    def export_orders_to_excel(self, path="orders_export.xlsx"):
        """Експортує всі замовлення з БД в Excel (без поля created_at)"""
        with self.db.conn.cursor() as cur:
            cur.execute("""
                SELECT title, description, city, price, url
                FROM orders_budver
                ORDER BY id DESC;
            """)
            rows = cur.fetchall()

        import pandas as pd
        df = pd.DataFrame(rows, columns=["Назва", "Опис", "Місто", "Бюджет", "Посилання"])
        df.to_excel(path, index=False)
        return path