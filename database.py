import psycopg2
from config import Config


class Database:
    """Класс, инкапсулирующий работу с PostgreSQL"""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.conn = psycopg2.connect(self.cfg.DB_URL)
        self.create_orders_table()

    def create_orders_table(self):
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

    def save_order(self, title, description, city, price, url):
        """Добавляет заказ, если его ещё нет в базе"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM orders_budver WHERE url = %s;", (url,))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO orders_budver (title, description, city, price, url)
                    VALUES (%s, %s, %s, %s, %s);
                """, (title, description, city, price, url))
                self.conn.commit()

    def drop_table(self, table_name: str):
        """
        Удаляет таблицу из базы данных, если она существует.
        ⚠️ Все данные будут безвозвратно удалены!
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
            self.conn.commit()
            print(f"🗑️ Таблиця '{table_name}' успішно видалена.")
        except Exception as e:
            print(f"❌ Помилка при видаленні таблиці '{table_name}': {e}")
        finally:
            # закрываем соединение, чтобы не зависло при ошибке
            if not self.conn.closed:
                self.conn.close()

    def check_exists(self, url: str) -> bool:
        """Проверяет, есть ли заказ с таким URL в базе"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1 FROM orders_budver WHERE url = %s;", (url,))
            return bool(cur.fetchone())
