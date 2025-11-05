import psycopg2
from config import Config


class Database:
    """Класс, инкапсулирующий работу с PostgreSQL"""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.conn = psycopg2.connect(self.cfg.DB_URL)
        self.create_all_tables()

    # ───────────────────────────────────────────────
    # 🗂️ Автоматическое создание всех нужных таблиц
    # ───────────────────────────────────────────────
    def create_all_tables(self):
        """Создаёт все необходимые таблицы, если их нет"""
        self.create_orders_budver_table()
        self.create_orders_rabotniki_table()

    def create_orders_budver_table(self):
        """Создаёт таблицу заказов Budver, если её нет"""
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

    # ───────────────────────────────────────────────
    # 🧩 Базовые CRUD методы
    # ───────────────────────────────────────────────
    def save_order(self, title, description, city, price, url, source="budver"):
        """Добавляет заказ в соответствующую таблицу, если его ещё нет"""
        table = "orders_budver" if source == "budver" else "orders_rabotniki"
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT id FROM {table} WHERE url = %s;", (url,))
            if not cur.fetchone():
                cur.execute(f"""
                    INSERT INTO {table} (title, description, city, price, url)
                    VALUES (%s, %s, %s, %s, %s);
                """, (title, description, city, price, url))
                self.conn.commit()

    def save_order_rabotniki(self, title, description, city, price, url):
        """Зберігає замовлення Rabotniki.ua"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM orders_rabotniki WHERE url = %s;", (url,))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO orders_rabotniki (title, description, city, price, url)
                    VALUES (%s, %s, %s, %s, %s);
                """, (title, description, city, price, url))
                self.conn.commit()

    def check_exists(self, url: str, source="budver") -> bool:
        """Проверяет, есть ли заказ с таким URL в указанной таблице"""
        table = "orders_budver" if source == "budver" else "orders_rabotniki"
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM {table} WHERE url = %s;", (url,))
            return bool(cur.fetchone())

    def drop_table(self, table_name: str):
        """Удаляет таблицу, если она существует"""
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
            self.conn.commit()
            print(f"🗑️ Таблиця '{table_name}' успішно видалена.")
        except Exception as e:
            print(f"❌ Помилка при видаленні таблиці '{table_name}': {e}")
        finally:
            if not self.conn.closed:
                self.conn.close()
