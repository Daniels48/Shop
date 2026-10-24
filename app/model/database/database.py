import psycopg2
from app.model.database import db_config
import datetime
from psycopg2 import sql

def get_local_time():
    return datetime.datetime.now()

class Database:
    def __init__(self):
        """Подключение к базе данных"""
        try:
            self.conn = psycopg2.connect(
                dbname=db_config.dbname,
                user=db_config.user,
                password=db_config.password,
                host=db_config.host,
                port=db_config.port
            )
            self.cursor = self.conn.cursor()
            # self.add_combined_payment_fields()

            # self.add_union_data_column()
            # self.remove_barcode_column_from_products()
            # self.change_quantity_to_decimal()



            print("Подключение к базе данных успешно!")

        except Exception as e:
            print("Ошибка подключения к базе данных:", e)
            raise


    def merge_products(self, main_product_id, secondary_product_id, quantity_to_add, union_data=None):
        """
        Объединяет товары:
        - добавляет переданное количество к основному товару,
        - переносит штрихкоды со вторичного товара,
        - обновляет product_id в inventory_changes и sale_items,
        - фиксирует изменение через add_inventory_changes с union_data,
        - удаляет вторичный товар.
        """
        try:
            # 1. Увеличиваем количество основного товара
            self.cursor.execute("""
                UPDATE products SET quantity = quantity + %s WHERE id = %s;
            """, (quantity_to_add, main_product_id))

            # 2. Переносим штрихкоды со вторичного товара
            self.cursor.execute("""
                UPDATE product_barcodes SET product_id = %s WHERE product_id = %s;
            """, (main_product_id, secondary_product_id))

            # 3. Обновляем product_id в связанных таблицах
            self.cursor.execute("""
                UPDATE inventory_changes SET product_id = %s WHERE product_id = %s;
            """, (main_product_id, secondary_product_id))
            self.cursor.execute("""
                UPDATE sale_items SET product_id = %s WHERE product_id = %s;
            """, (main_product_id, secondary_product_id))

            # 4. Удаляем вторичный товар
            self.cursor.execute("DELETE FROM products WHERE id = %s;", (secondary_product_id,))

            # 5. Фиксируем изменение в inventory_changes
            self.add_inventory_changes(
                product_id=main_product_id,
                quantity=quantity_to_add,
                type_action='union',
                union_data=union_data
            )

            # 7. Сохраняем изменения
            self.conn.commit()
            print(f"✅ Объединение завершено: товар {secondary_product_id} → {main_product_id}, +{quantity_to_add}")
            return True

        except Exception as e:
            self.conn.rollback()
            print(f"❌ Ошибка при объединении товаров: {e}")
            return False

    def get_product_id_by_name(self, product_name):
        """Получает product_id по названию товара."""
        try:
            self.cursor.execute("SELECT id FROM products WHERE name = %s;", (product_name,))
            product_id = self.cursor.fetchone()
            return product_id[0] if product_id else None
        except Exception as e:
            print(f"Ошибка при получении product_id по имени товара: {e}")
            return None

    def get_inventory_summary(self):
        """Получение статистики по количеству товаров, сумме товаров и стоимости товаров"""
        try:
            # Подсчет общего количества товаров
            self.cursor.execute("SELECT SUM(quantity) FROM products;")
            total_quantity = self.cursor.fetchone()[0] or 0

            # Подсчет суммы всех товаров
            self.cursor.execute("SELECT SUM(quantity * price_sale) FROM products;")
            total_value = self.cursor.fetchone()[0] or 0

            # Подсчет общего количества товаров (количество строк)
            self.cursor.execute("SELECT COUNT(*) FROM products;")
            total_items = self.cursor.fetchone()[0]

            return total_items, total_quantity, total_value
        except Exception as e:
            print("Ошибка при получении статистики инвентаря:", e)
            return 0, 0, 0

    def barcode_exists(self, barcode):
        """Проверяет наличие штрих-кода в таблице product_barcodes"""
        try:
            self.cursor.execute("SELECT 1 FROM product_barcodes WHERE barcode = %s LIMIT 1;", (barcode,))
            return self.cursor.fetchone() is not None
        except Exception as e:
            print("Ошибка при проверке штрих-кода:", e)
            return False

    def get_all_barcodes(self):
        """Получает список всех штрих-кодов из базы данных"""
        try:
            self.cursor.execute("SELECT barcode FROM product_barcodes;")
            barcodes = [row[0] for row in self.cursor.fetchall()]
            return barcodes
        except Exception as e:
            print("Ошибка при получении штрих-кодов:", e)
            return []

    # Method for getting action details for product
    def get_action_details(self, record_id, is_sale=True):
        """Получает подробную информацию о конкретной продаже или изменении товара.
        :param action_type: Тип запроса ('sale' для продажи, 'inventory_change' для изменения товара)
        :param record_id: ID записи (sale_id или id из inventory_changes)
        :return: Детальная информация о продаже или изменении товара
        """

        try:
            if is_sale:
                # Запрос детальной информации о конкретной продаже
                self.cursor.execute("""
                    SELECT 
                    
                        s.id AS sale_id,
                        s.sale_date,
                        s.payment_method,
                        p.name AS product_name,
                        si.quantity,
                        si.item_price
                        
                    FROM sale_items si
                    JOIN sales s ON si.sale_id = s.id
                    JOIN products p ON si.product_id = p.id
                    WHERE s.id = %s;
                """, (record_id,))
                details = self.cursor.fetchall()
            #     id_sale,date,type_method,name,quantity,price

            else:
                # Запрос детальной информации об изменении товара
                self.cursor.execute("""
                    SELECT 
                    
                        ic.id AS change_id,
                        ic.change_date,
                        ic.type_action,
                        p.name AS product_name,
                        ic.quantity,
                        ic.union_data
                        
                    FROM inventory_changes ic
                    JOIN products p ON ic.product_id = p.id
                    WHERE ic.id = %s;
                """, (record_id,))
                details = self.cursor.fetchall()
            #     id_change,date,type_action,name,quantity

            return details

        except Exception as e:
            print(f"Ошибка при получении деталей действия: {e}")
            return None

    # Method for getting all products and sorting
    def get_all_products(self, sort_by="id", ascending=True, barcode=None):
        """
        📦 Получает список всех товаров с возможностью сортировки по выбранному столбцу
        или одного товара по его штрих-коду. Возвращает все штрих-коды, связанные с товаром,
        в виде строки, разделённой ";"
        """
        try:
            order = "ASC" if ascending else "DESC"

            sort_by = sort_by + "s" if sort_by == "barcode" else sort_by

            if barcode:
                self.cursor.execute("""
                    SELECT 
                        p.id, 
                        p.name, 
                        STRING_AGG(pb.barcode, ';') AS barcodes,
                        p.price_sale,
                        p.quantity
                    FROM products p
                    LEFT JOIN product_barcodes pb ON pb.product_id = p.id
                    WHERE pb.barcode = %s
                    GROUP BY p.id
                """, (barcode,))
            else:
                self.cursor.execute(f"""
                    SELECT 
                        p.id, 
                        p.name, 
                        STRING_AGG(pb.barcode, ';') AS barcodes,
                        p.price_sale,
                        p.quantity
                    FROM products p
                    LEFT JOIN product_barcodes pb ON pb.product_id = p.id
                    GROUP BY p.id
                    ORDER BY {sort_by} {order};
                """)

            products = self.cursor.fetchall()
            return products  # [(id, name, "barcode1;barcode2", price_sale, quantity)]

        except Exception as e:
            print(f"Ошибка при получении списка товаров: {e}")
            return []

    def get_available_months(self, barcode_product: str = None) -> list:
        """Возвращает список месяцев, в которых есть изменения. Фильтруется по штрих-коду, если указан."""
        try:
            params = []
            where_clause = ""

            if barcode_product:
                where_clause = "WHERE pb.barcode = %s"
                params.append(barcode_product)

            query = f"""
                SELECT DISTINCT TO_CHAR(ic.change_date, 'YYYY-MM') AS month_str
                FROM inventory_changes ic
                JOIN products p ON ic.product_id = p.id
                JOIN product_barcodes pb ON pb.product_id = p.id
                {where_clause}
                ORDER BY month_str DESC
            """
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            return [row[0] for row in rows]

        except Exception as e:
            print(f"❌ Ошибка при получении месяцев: {e}")
            return []

    # Method for getting all inventory changes
    def get_inventory_changes(self, barcode_product: str = None, date_range: tuple = None) -> list:
        """
        Возвращает строки инвентарных изменений.
        :param barcode_product:  штрих‑код товара или None
        :param date_range:       ('YYYY-MM-DD', 'YYYY-MM-DD') — обязательно
        :return:                 list[tuple] — строки выборки
        """
        if not date_range:
            raise ValueError("Параметр date_range обязателен")

        # ——— Подготовка «постоянных» параметров ———
        lunch_codes = [
            "2117674458339", "2967148931185", "2627451727683",
            "5581777172473", "3828139792736",
        ]
        codes_ph = ",".join(["%s"] * len(lunch_codes))

        filters, params = [], lunch_codes.copy()

        # ——— Фильтр по диапазону дат ———
        start_date, end_date = date_range
        filters.append("ic.change_date >= %s AND ic.change_date < %s")
        params.extend([start_date, end_date])

        # ——— Фильтр по штрих‑коду (опционально) ———
        if barcode_product:
            filters.append("pb.barcode = %s")
            params.append(barcode_product)

        where_clause = " WHERE " + " AND ".join(filters)

        query_sum = f"""CASE
                    WHEN ic.type_action = 'sale' THEN s.total_amount
                    WHEN ic.type_action = 'union' THEN 0
                    ELSE ic.quantity * COALESCE(p.price_sale, 0)
                  END"""

        query_quantity = """
                CASE 
                    WHEN ic.type_action = 'sale' THEN (
                      SELECT COALESCE(SUM(si2.quantity), 0)
                        FROM sale_items si2
                      WHERE si2.sale_id = s.id
                    )
                    ELSE ic.quantity
                  END"""

        query_sum_lunch = f"""(SELECT COALESCE(SUM(si3.quantity * si3.item_price), 0.0::numeric)
                   FROM sale_items si3
                   JOIN products        p3  ON si3.product_id = p3.id
                   JOIN product_barcodes pb3 ON pb3.product_id = p3.id
                  WHERE si3.sale_id = s.id
                    AND pb3.barcode IN ({codes_ph}))"""

        query = f"""
            SELECT DISTINCT
                ic.type_action         AS "Действие",
                s.payment_method       AS "Тип_продажи",
                {query_sum}            AS "Сумма",                  
                {query_quantity}       AS "Кол-во",
                ic.change_date         AS "Время",
                ic.id                  AS change_id,
                s.id                   AS sale_id,
                s.cash_combine         AS cash_amount_combine,
                s.card_combine         AS card_amount_combine,
                {query_sum_lunch}      AS lunch_amount

            FROM inventory_changes ic
            LEFT JOIN sales            s  ON ic.id_sale   = s.id
            LEFT JOIN products         p  ON ic.product_id = p.id
            LEFT JOIN product_barcodes pb ON pb.product_id = p.id
            {where_clause}
            ORDER BY ic.change_date DESC;
        """

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def search_products(self, search_text):
        """🔍 Ищет товары по названию или штрих-коду, возвращает сгруппированные штрих-коды"""
        try:
            self.cursor.execute("""
                SELECT 
                    STRING_AGG(pb.barcode, ';') AS barcodes,
                    p.name,
                    p.quantity,
                    p.price_sale,
                    p.id
                FROM products p
                LEFT JOIN product_barcodes pb ON pb.product_id = p.id
                WHERE LOWER(p.name) LIKE %s OR pb.barcode LIKE %s
                GROUP BY p.id
                LIMIT 8;
            """, (f"%{search_text.lower()}%", f"%{search_text}%"))

            results = self.cursor.fetchall()  # [(barcode1;barcode2, name, quantity, price_sale, id)]
            return results

        except Exception as e:
            print(f"Ошибка при поиске товара: {e}")
            return []

    # MAIN Method for add new product
    def add_new_product(self, barcodes: list, name: str, price_sale: float, quantity: float):
        """
        Добавляет новый товар в таблицу products, связывает с несколькими штрих-кодами,
        и записывает изменения в inventory_changes.
        Все операции выполняются в рамках одной транзакции.

        :param barcodes: список штрих-кодов
        :param name: название товара
        :param price_sale: цена продажи
        :param quantity: количество
        :return: product_id или None
        """
        try:
            if not barcodes:
                print("Не передан ни один штрих-код.")
                return None

            # Начинаем транзакцию
            self.cursor.execute("""
                INSERT INTO products (name, price_sale, quantity)
                VALUES (%s, %s, %s) RETURNING id;
            """, (name, price_sale, quantity))

            product_id = self.cursor.fetchone()[0]

            # Вставляем штрих-коды в таблицу product_barcodes
            for barcode in barcodes:
                self.cursor.execute("""
                    INSERT INTO product_barcodes (product_id, barcode)
                    VALUES (%s, %s);
                """, (product_id, barcode))

            # Добавляем запись в историю изменений
            self.add_inventory_changes(product_id, quantity, type_action="new_item")

            self.conn.commit()
            print(f"✅ Товар с ID {product_id} добавлен. Штрих-коды: {', '.join(barcodes)}")
            return product_id

        except Exception as e:
            self.conn.rollback()
            print(f"❌ Ошибка при добавлении нового товара: {e}")
            return None

    # ----------------------------------------------------------

    # MAIN Method for clear quantity product
    def clear_quantity_product(self, product_id, quantity):
        try:
            # Начало транзакции
            type_action = 'clear'  # Тип действия - списание товара
            self.update_quantity_product(product_id, quantity, type_action)
            self.add_inventory_changes(product_id, quantity, type_action)

            # Завершаем транзакцию
            self.conn.commit()
            print(f"Товар с ID {product_id} успешно обновлен")
            return True

        except Exception as e:
            self.conn.rollback()  # Откат транзакции в случае ошибки
            print(e)
            return None
    # ----------------------------------------------------------

    # MAIN Method for getting product by barcode
    def get_product_by_barcode(self, barcode):
        """Получает информацию о товаре по штрих-коду из связанной таблицы product_barcodes."""
        try:
            self.cursor.execute("""
                SELECT 
                    STRING_AGG(pb.barcode, ';') AS barcodes,
                    p.name,
                    p.quantity,
                    p.price_sale,
                    p.id
                FROM product_barcodes pb
                JOIN products p ON pb.product_id = p.id
                WHERE pb.barcode = %s
                GROUP BY p.id;
            """, (barcode,))

            result = self.cursor.fetchone()  # (barcode1;barcode2, name, quantity, price_sale, id)
            if result:
                return result
            else:
                print(f"Товар с штрих-кодом {barcode} не найден.")
                return None

        except Exception as e:
            print(f"Ошибка при получении товара: {e}")
            return None

    # --------------------------------------------

    # MAIN Methods for update date product
    def update_all_fields(self,barcode, updates):
        new_updates = {}
        try:
            # Начало транзакции

            product_id = self.get_product_by_barcode(barcode)[-1]  # Получаем ID

            # Добавляем запись об изменении инвентаря в таблицу inventory_changes
            type_action = 'add'  # Тип действия - добавление товара

            if updates.get("name"):
                new_updates["name"] = self.update_name_product(product_id, updates["name"])

            # if updates.get("barcode"):
            #     new_updates["barcode"] = self.update_barcode_product(product_id, updates["barcode"])

            if updates.get("quantity"):
                new_updates["quantity"] = self.update_quantity_product(product_id, updates["quantity"],type_action)
                self.add_inventory_changes(product_id, updates["quantity"], type_action)

            if updates.get("price"):
                new_updates["price"] = self.update_price_product(product_id, updates["price"])


            # Завершаем транзакцию
            self.conn.commit()
            print(f"Товар с ID {product_id} успешно обновлен")
            return new_updates

        except Exception as e:
            self.conn.rollback()  # Откат транзакции в случае ошибки
            print(e)
            return None



    def update_name_product(self, product_id, name):
        self.cursor.execute(f"""
            UPDATE products
            SET name = %s
            WHERE id = %s;
        """, (name, product_id))
        return True

    # def update_barcode_product(self, product_id, barcode):
    #     self.cursor.execute(f"""
    #         UPDATE products
    #         SET barcode = %s
    #         WHERE id = %s;
    #     """, (barcode, product_id))
    #     return True

    def update_price_product(self, product_id, price_sale):
        self.cursor.execute(f"""
            UPDATE products
            SET price_sale = %s
            WHERE id = %s;
        """, (price_sale, product_id))
        return True
    # ----------------------------------------------------------------------------

    # Method for add inventory changes
    def add_inventory_changes(self, product_id, quantity, type_action, sale_id=None, union_data=None):
        # Добавляем запись в inventory_changes (id_sale = NULL)
        time_loc = get_local_time()
        self.cursor.execute("""
            INSERT INTO inventory_changes (product_id, quantity, type_action, id_sale, union_data, change_date)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (product_id, quantity, type_action, sale_id, union_data, time_loc))

    # Method for add date sale
    def add_sale_with_items(self, total_amount, payment_method, products, is_barcode=True, cash_combine=None,
                            card_combine=None):
        """
        Добавляет запись о продаже в таблицу sales, товары в sale_items,
        а также обновляет количество товаров и добавляет запись в inventory_changes.
        Поддерживает комбинированную оплату (payment_method = 'combined').
        Все операции выполняются в рамках одной транзакции.
        """
        try:
            type_action = "sale"
            sale_date = get_local_time()

            # Выбираем SQL-запрос в зависимости от способа оплаты
            if payment_method == "combined":
                self.cursor.execute("""
                    INSERT INTO sales (sale_date, total_amount, payment_method, cash_combine, card_combine)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                """, (sale_date, total_amount, payment_method, cash_combine, card_combine))
            else:
                self.cursor.execute("""
                    INSERT INTO sales (sale_date, total_amount, payment_method)
                    VALUES (%s, %s, %s)
                    RETURNING id;
                """, (sale_date, total_amount, payment_method))

            sale_id = self.cursor.fetchone()[0]

            # Обработка каждого товара
            for product in products:
                product_id = product.id
                quantity = product.current_quantity
                price = product.price

                # Добавляем товар в sale_items
                self.cursor.execute("""
                    INSERT INTO sale_items (sale_id, product_id, quantity, item_price)
                    VALUES (%s, %s, %s, %s);
                """, (sale_id, product_id, quantity, price))

                # Обновляем остаток
                if is_barcode:
                    self.update_quantity_product(product_id, quantity, type_action)

                # Добавляем запись в inventory_changes
                self.add_inventory_changes(product_id, quantity, type_action, sale_id)

            self.conn.commit()
            print(f"Продажа успешно добавлена с ID {sale_id}")
            return sale_id

        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при обработке продажи: {e}")
            return None

    def update_quantity_product(self,product_id, quantity, type_action):
        # Обновляем количество товара в таблице products
        sign = "+" if type_action == "add" else "-"

        self.cursor.execute(f"""
            UPDATE products
            SET quantity = quantity {sign} %s
            WHERE id = %s;
        """, (quantity, product_id))
        return True

    # Method for getting check number
    def get_next_sale_number(self):
        """
        Получает максимальное значение id из таблицы sales, увеличивает его на 1.
        Если записей нет, возвращает 1.
        """
        try:
            self.cursor.execute("SELECT MAX(id) FROM sales;")
            result = self.cursor.fetchone()[0]
            if result is None:
                return 1
            return result + 1
        except Exception as e:
            print(f"Ошибка при получении номера продажи: {e}")
            return 1

    # Method for close connection on base date
    def close_connection(self):
        """Закрытие соединения с базой данных."""
        self.cursor.close()
        self.conn.close()
        print("Соединение с базой данных закрыто.")




        # def update_existing_records(self, table_name, column_name):
        #     """Обновляет уже существующие записи, добавляя +2 часа"""
        #     try:
        #         query = f"""
        #             UPDATE {table_name}
        #             SET {column_name} = {column_name} + INTERVAL '2 hours';
        #         """
        #         self.cursor.execute(query)
        #         self.conn.commit()
        #         print(f"Время обновлено во всех существующих записях в таблице {table_name}.")
        #     except Exception as e:
        #         print(f"Ошибка при обновлении записей в {table_name}:", e)
    # def set_default_time(self, table_name, column_name):
    #     """Изменяет значение по умолчанию, добавляя +2 часа к CURRENT_TIMESTAMP"""
    #     try:
    #         query = f"""
    #             ALTER TABLE {table_name}
    #             ALTER COLUMN {column_name}
    #             SET DEFAULT CURRENT_TIMESTAMP + INTERVAL '2 hours';
    #         """
    #         self.cursor.execute(query)
    #         self.conn.commit()
    #         print(f"Новое значение по умолчанию установлено для {column_name} в {table_name}.")
    #     except Exception as e:
    #         print(f"Ошибка при изменении значения по умолчанию в {table_name}:", e)
    # def change_quantity_to_decimal(self):
    #     """Меняет тип quantity в нужных таблицах на DECIMAL(10,2)"""
    #     tables = ["products", "sale_items", "inventory_changes"]
    #
    #     try:
    #         for table in tables:
    #             print(f"Изменение типа quantity в таблице {table}...")
    #
    #             self.cursor.execute(sql.SQL("""
    #                 ALTER TABLE {} ALTER COLUMN quantity TYPE DECIMAL(10,2) USING quantity::DECIMAL(10,2);
    #             """).format(sql.Identifier(table)))
    #
    #         self.conn.commit()
    #         print("Столбцы quantity успешно изменены на DECIMAL(10,2).")
    #
    #     except Exception as e:
    #         self.conn.rollback()
    #         print(f"Ошибка при изменении типа данных: {e}")