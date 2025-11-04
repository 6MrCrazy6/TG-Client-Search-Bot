from database import Database
from parsers.budver_parser import parse_budver_kyiv_repairs

class OrderService:
    """Бизнес-логика: парсинг, фильтрация, сохранение"""

    def __init__(self, db: Database):
        self.db = db

    async def fetch_and_save_orders(self):
        """Асинхронно загружает заказы и сохраняет их"""
        orders = await parse_budver_kyiv_repairs(max_pages=3)  # можно задать сколько страниц
        for o in orders:
            self.db.save_order(o["title"], o["desc"], o["city"], o["price"], o["url"])
        return orders
