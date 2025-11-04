from database import Database
from parsers.budver_parser import BudverParser

class OrderService:
    """Бизнес-логика: парсинг, фильтрация, сохранение"""

    def __init__(self, db: Database):
        self.db = db
        self.parser = BudverParser()

    def fetch_and_save_orders(self):
        """Загружает заказы и сохраняет их"""
        orders = self.parser.fetch_orders()
        for o in orders:
            self.db.save_order(o["title"], o["desc"], o["city"], o["price"], o["url"])
        return orders
