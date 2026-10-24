from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QMessageBox
from PyQt5.QtCore import Qt


POSITION_CONFIG = {
    'main': dict(offset_x=+24, offset_y=67, extra_width=1110),
    'product': dict(offset_x=13, offset_y=77),
    'history': dict(offset_x=550, offset_y=12),
    'print': dict(offset_x=13, offset_y=20),
}

def get_product_and_handle(product_value, field, db, on_success: callable, on_fail: callable = None):
    """
    Загружает товар по штрих-коду из поля или напрямую, если уже передан product_value.

    :param product_value: кортеж данных товара или None/False
    :param field: QLineEdit — поле, из которого берётся штрих-код
    :param db: объект базы данных с методом get_product_by_barcode(barcode)
    :param on_success: функция, вызываемая при успешной загрузке (product)
    :param on_fail: функция, вызываемая при ошибке (опционально)
    """
    try:
        # Если товар уже передан (например, из списка) — используем его
        if product_value:
            on_success(product_value)
            field.setText("")
            field.setFocus()
            return

        barcode = field.text().strip()
        product = db.get_product_by_barcode(barcode)


        if not product:

            QMessageBox.warning(field.parent(), "Ошибка", f"Продукт с данным {barcode} не найден!")
            field.setText("")
            field.setFocus()
            if on_fail:
                on_fail()

            return

        on_success(product)
        field.setText("")
        field.setFocus()


    except Exception as e:
        print(f"[load_product_by_input] Ошибка: {e}")


def create_search_result_list(dialog, input_field):
    """
    Создаёт выпадающий список результатов поиска (QListWidget),
    который располагается поверх указанного поля ввода.

    :param input_field: QLineEdit или другой виджет, относительно которого позиционируется список
    :return: настроенный и скрытый по умолчанию QListWidget
    """
    try:
        result_list = QListWidget(dialog)
        result_list.setVisible(False)
        result_list.setStyleSheet("""
            QListWidget {
                background: white;
                border: 2px solid #73B5E7;
                border-radius: 10px;
                font-size: 22px;
            }
            QListWidget::item {
                padding: 8px 0;
                height: 40px;
                border-bottom: 2px solid black;
            }
            QListWidget::item:hover {
                border-bottom: none;
                border-radius: 10px;
                background-color: #01B4E4;
            }
            QListWidget::item:selected {
                background-color: #01B4E4;
                color: white;
            }
            QListWidget:focus-within QListWidget::item:selected {
                background-color: #0078D7;
            }
            QListWidget:!focus QListWidget::item:selected {
                background-color: #e0e0e0;
                color: black;
            }
        """)

        # Расположение списка прямо под полем ввода
        result_list.setParent(dialog)
        result_list.setGeometry(
            input_field.x(),
            input_field.y() + input_field.height(),
            input_field.width(),
            1000  # Фиксированная максимальная высота
        )
        result_list.raise_()
        return result_list

    except Exception as e:
        print(f"[create_search_result_list] Error: {e}")

#------------------------------------------
def update_list_position(
    item_count=0,
    input_field=None,
    list_result=None,
    offset_x=0,
    offset_y=0,
    extra_width=0
):
    """
    📌 Обновляет размер и позицию выпадающего списка результатов поиска.

    :param item_count: количество элементов в списке
    :param input_field: поле ввода (QLineEdit)
    :param list_result: QListWidget — сам выпадающий список
    :param offset_x: смещение по горизонтали (влево/вправо)
    :param offset_y: смещение вниз от поля ввода
    :param extra_width: добавить ширину к списку
    """
    try:
        x = input_field.x() + offset_x
        y = input_field.y() + input_field.height() + offset_y
        width = input_field.width() + extra_width

        max_items = 8
        item_height = list_result.sizeHintForRow(0) if list_result.count() > 0 else 33
        padding = 8
        height = min(item_count, max_items) * item_height + padding

        list_result.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        list_result.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        list_result.move(x, y)
        list_result.resize(width, height)
        list_result.raise_()

    except Exception as e:
        print(f"[update_list_position] {e}")
#------------------------------------------------------------
def update_results(db, input_field, list_result, offset_x=0, offset_y=0, extra_width=0):
    """🔍 Обновляет список товаров по введённому тексту и позиционирует выпадающий список."""
    try:
        text = input_field.text().strip()
        if not text:
            list_result.clear()
            list_result.setVisible(False)
            return

        results = db.search_products(text)  # Поиск товаров

        list_result.clear()
        if results:
            for barcode, name, quantity, price, id in results:
                item_text = f"{name} - {price} руб, {quantity} шт.(кг)."
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, {
                    'data': (barcode, name, quantity, price, id)
                })
                list_result.addItem(item)

            list_result.setVisible(True)

            # 📌 Обновляем положение списка
            update_list_position(
                item_count=len(results),
                input_field=input_field,
                list_result=list_result,
                offset_x=offset_x,
                offset_y=offset_y,
                extra_width=extra_width
            )

        else:
            list_result.setVisible(False)

    except Exception as e:
        print(f"[update_results] Ошибка: {e}")
#----------------------------
def select_current_item(list_result, handler_function, is_main=False):
    """
    Универсальный выбор текущего элемента из QListWidget.

    :param list_result: QListWidget с результатами.
    :param handler_function: функция обработки товара.
    :param is_main: если True, передаём штрихкод и is_manual.
    """
    current_item = list_result.currentItem()

    if not current_item:
        print("[select_current_item] Нет выбранного элемента")
        return

    try:
        product_data = current_item.data(Qt.UserRole)

        if not product_data or "data" not in product_data:
            print(
                "[select_current_item] Данные в item некорректны:",
                product_data,
            )
            return

        product = product_data["data"]

        if is_main:
            barcode = product[0].split(";")[0]

            # Вызываем синхронный обработчик событий,
            # который сам запустит асинхронный метод презентера.
            handler_function(
                barcode_transfer=barcode,
                is_manual=True,
            )
        else:
            handler_function(product)

    except Exception as e:
        print(f"[select_current_item] Ошибка при выборе: {e}")

    finally:
        list_result.setVisible(False)

