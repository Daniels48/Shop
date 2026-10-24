import psycopg2
from psycopg2 import sql
from Db_postgres import db_config


def setup_database():

    # Настройки для подключения к PostgreSQL (под суперпользователем postgres)
    DB_ADMIN_CONFIG = {
        "dbname": db_config.dbname2,  # Подключаемся к системной базе данных
        "user": db_config.user,  # Имя суперпользователя
        "password": db_config.password,  # Укажите ваш пароль суперпользователя
        "host": db_config.host,
        "port": db_config.port
    }

    try:
        # Подключаемся к PostgreSQL
        conn = psycopg2.connect(**DB_ADMIN_CONFIG)
        conn.autocommit = True  # Включаем autocommit для работы с CREATE DATABASE
        cursor = conn.cursor()

        # 1. Создаем новую базу данных
        database_name = db_config.dbname
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
        print(f"База данных '{database_name}' успешно создана.")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

def create_tables():
    # Подключение к базе данных PostgreSQL
    DB_CONFIG = {
        "dbname": db_config.dbname,  # Подключаемся к системной базе данных
        "user": db_config.user,      # Имя пользователя
        "password": db_config.password,
        "host": db_config.host,
        "port": db_config.port
    }

    try:
        # Подключение к базе данных
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Создание таблицы products
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                barcode VARCHAR(100) UNIQUE NOT NULL,
                price_sale DECIMAL(10, 2) NOT NULL,
                quantity DECIMAL(10, 2) NOT NULL DEFAULT 1
            );
        """)

        # Создание таблицы sales
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id SERIAL PRIMARY KEY,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount DECIMAL(10, 2) NOT NULL,
                payment_method VARCHAR(50) NOT NULL
            );
        """)

        # Создание таблицы sale_items
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sale_items (
                id SERIAL PRIMARY KEY,
                sale_id INTEGER REFERENCES sales(id) ON DELETE CASCADE,
                product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                quantity DECIMAL(10, 2) NOT NULL,
                item_price DECIMAL(10, 2) NOT NULL
            );
        """)

        # Создание таблицы inventory_changes с дополнительной колонкой cashier
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory_changes (
                id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                quantity DECIMAL(10, 2) NOT NULL,
                change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                type_action VARCHAR(50) NOT NULL,
                id_sale INTEGER REFERENCES sales(id) ON DELETE SET NULL
            );
        """)

        # Создание индексов для ускорения запросов:

        ## Таблица products
        # Индекс для поиска по name (если часто ищут по наименованию)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);")

        ## Таблица sales
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_sale_date ON sales(sale_date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_payment_method ON sales(payment_method);")

        ## Таблица sale_items
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sale_items_sale_id ON sale_items(sale_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sale_items_product_id ON sale_items(product_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sale_items_sale_product ON sale_items(sale_id, product_id);")

        ## Таблица inventory_changes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_changes_product_id ON inventory_changes(product_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_changes_change_date ON inventory_changes(change_date);")

        # Подтверждение изменений и завершение транзакции
        conn.commit()
        print("Все таблицы и индексы успешно созданы.")

    except Exception as e:
        print(f"Ошибка при создании таблиц или индексов: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

def delete_database(db_name, user, password, host, port):
    try:
        # Подключаемся к системной базе данных (обычно 'postgres')
        conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host, port=port)
        conn.autocommit = True  # Устанавливаем режим autocommit

        cur = conn.cursor()

        # Завершаем активные подключения к базе
        cur.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}' AND pid <> pg_backend_pid();
        """)

        # Удаляем базу данных
        cur.execute(f"DROP DATABASE {db_name};")

        print(f"База данных {db_name} успешно удалена.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Ошибка при удалении базы данных: {e}")

def create_or_delete_base(create=True):
    if create:
        # Выполняем настройку
        setup_database()

        # Вызов функции для создания таблиц и индексов
        create_tables()
    else:
        # Пример вызова функции
        delete_database(db_config.dbname, db_config.user, db_config.password, db_config.host, db_config.port)

create_or_delete_base(True)





