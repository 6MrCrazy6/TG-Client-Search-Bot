import psycopg2
from config import Config

class Database:
    """Класс, инкапсулирующий работу с PostgreSQL"""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.conn = psycopg2.connect(self.cfg.DB_URL)
        self.create_orders_table()

    def create_orders_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders_budver (
                    id SERIAL PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    city TEXT,
                    price TEXT,
                    url TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
        self.conn.commit()

    def save_order(self, title, description, city, price, url):
        """Добавляет заказ, если он новый"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM orders_budver WHERE url = %s;", (url,))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO orders_budver (title, description, city, price, url)
                    VALUES (%s, %s, %s, %s, %s);
                """, (title, description, city, price, url))
                self.conn.commit()
