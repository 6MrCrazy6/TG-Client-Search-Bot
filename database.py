import psycopg2
from config import Config


class Database:
    """Клас для роботи з PostgreSQL (Budver, Rabotniki, Kabanchik)"""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.conn = psycopg2.connect(self.cfg.DB_URL)
        self.create_all_tables()

    # ────────────────────────────────
    # 🗂️ Автоматичне створення таблиць
    # ────────────────────────────────
    def create_all_tables(self):
        self.create_orders_budver_table()
        self.create_orders_rabotniki_table()
        self.create_orders_kabanchik_table()

    def create_orders_budver_table(self):
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

    def create_orders_rabotniki_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders_rabotniki (
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

    def create_orders_kabanchik_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders_kabanchik (
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

    # ────────────────────────────────
    # 🧩 Збереження замовлень
    # ────────────────────────────────
    def save_order(self, title, description, city, price, url, source="budver"):
        if not url:
            print(f"⚠️ Пропуск запису — відсутній URL ({source})")
            return

        table_map = {
            "budver": "orders_budver",
            "rabotniki": "orders_rabotniki",
            "kabanchik": "orders_kabanchik"
        }
        table = table_map.get(source, "orders_budver")

        with self.conn.cursor() as cur:
            cur.execute(f"SELECT id FROM {table} WHERE url = %s;", (url,))
            if not cur.fetchone():
                cur.execute(f"""
                    INSERT INTO {table} (title, description, city, price, url)
                    VALUES (%s, %s, %s, %s, %s);
                """, (
                    title or "—",
                    description or "—",
                    city or "—",
                    price or "—",
                    url
                ))
                self.conn.commit()

    # ✅ Оставляем для сумісності старий виклик:
    def save_order_rabotniki(self, title, description, city, price, url):
        """Alias для Rabotniki.ua (сумісність зі старим кодом)"""
        self.save_order(title, description, city, price, url, source="rabotniki")

    def check_exists(self, url: str, source="budver") -> bool:
        """Перевіряє, чи існує замовлення"""
        table_map = {
            "budver": "orders_budver",
            "rabotniki": "orders_rabotniki",
            "kabanchik": "orders_kabanchik"
        }
        table = table_map.get(source, "orders_budver")

        with self.conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM {table} WHERE url = %s;", (url,))
            return bool(cur.fetchone())

    def drop_table(self, table_name: str):
        """Видаляє таблицю"""
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
            self.conn.commit()
            print(f"🗑️ Таблиця '{table_name}' видалена.")
        except Exception as e:
            print(f"❌ Помилка при видаленні таблиці '{table_name}': {e}")
