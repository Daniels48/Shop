# import threading
# from PyQt5.QtWidgets import QListWidget, QListWidgetItem
# from PyQt5.QtCore import Qt
# from presenter.pc2 import Mock1CServer
# import asyncio
from app.db.database import SessionLocal
from app.db.repositories.sale_repository import SaleRepository
from app.model.ProductModel import Product
from app.model.database.database import Database
from app.utils.decorators import handle_dialog
from app.view.dialog import ProductDialog, DataDialog, PaymentDialog, PayDialog, CountDialog, PrintDialog
from app.search_global import update_results, POSITION_CONFIG, select_current_item


class MainPresenter:
    def __init__(self, main_window):
        self.main_window = main_window

        # Настройка программы и переменные
        self.total_sum = 0
        self.db = Database()
        self.name_ = "Отсканируйте товар"
        self.width_number = 70
        self.width_price = 150
        self.width_count = 150
        self.width_sum = 150

        with SessionLocal() as session:
            rep = SaleRepository(session)
            self.number_check = rep.get_next_sale_number()

        # self.number_check = self.db.get_next_sale_number()

    @handle_dialog
    def open_barcode_print_dialog(self):
        dialog = PrintDialog(self.db)
        dialog.exec_()  # Используем exec_() в PyQt5

    # Pay Dialog
    @handle_dialog
    def open_payment_dialog(self):
        if self.total_sum <= 0:
            return

        payment_dialog = PaymentDialog(self.total_sum, self.number_check)
        if payment_dialog.exec_():  # Если успешно закрыли диалог (что-то купили)
            selected_method = payment_dialog.get_selected_method()  # метод оплаты

            if selected_method:
                is_combined = selected_method == "combined"


                self.db.add_sale_with_items(
                    total_amount=self.total_sum,
                    payment_method=selected_method,
                    products=self.main_window.left_panel.product_model.get_product_list(),
                    cash_combine=payment_dialog.get_cash_combine() if is_combined else None,
                    card_combine=payment_dialog.get_card_combine() if is_combined else None
                )

                self.update_check_number()
                self.clear_table()

    # Pay card Dialog
    @handle_dialog
    def open_manual_payment_dialog(self):
        dialog = PayDialog()
        if dialog.exec_():  # Используем exec_() в PyQt5
            payment_method = dialog.get_payment_method()
            total_amount = dialog.get_value()
            products = [Product(id="1022", quantity=1, price=total_amount, name="Товар без штрих-кода", barcode="0",
                                main_window=self)]
            self.db.add_sale_with_items(total_amount, payment_method, products, False)
            self.update_check_number()
            self.clear_table()

    @handle_dialog
    def open_product_dialog(self):
        self.clear_table()
        # with SessionLocal() as session:
        #     rep = SaleRepository(session)
        #     self.number_check = rep.get_next_sale_number()
        dialog = ProductDialog(parent=self.main_window,db=self.db)
        dialog.exec_()

    @handle_dialog
    def open_quantity_dialog(self):
        """Метод для изменения количества товара"""
        row = self.main_window.left_panel.product_model.get_selected_row()
        # Если строка не выбрана или индекс некорректен
        if row is not None:
            dialog = CountDialog(self.main_window)
            if dialog.exec_():  # Используем exec_() в PyQt5
                value = float(dialog.get_value())
                # Получаем индекс выделенной строки
                product = self.main_window.left_panel.product_model._products[row]  # Получаем продукт на основе индекса
                if product:
                    product.set_quantity(value)  # Обновляем количество товара
                    self.main_window.left_panel.table_view.viewport().update()
                    self.update_total()  # При необходимости пересчитываем общую сумму

    # Last action Dialog
    @handle_dialog
    def open_last_action_dialog(self):
        last_action_dialog = DataDialog(self.db)
        last_action_dialog.exec_()

    # -------------------------------------------------------------------------
    def overlay_on(self):
        self.main_window.overlay.setVisible(True)

    def overlay_off(self):
        self.main_window.overlay.setVisible(False)

    def focus_table(self):
        self.main_window.left_panel.table_view.setFocus()
    # -------------------------------------------------------------------------------------

    def prepare_barcode_input(self, barcode_transfer=None, is_manual=False):
        input_value = None
        barcode = self.main_window.right_panel.barcode_edit
        old_text_input_barcode_edit = barcode.text().strip()
        if barcode_transfer:
            input_value = barcode_transfer
            if is_manual:
                previous_focus_widget = self.main_window.focusWidget()  # Сохраняем предыдущий фокус
                cursor_position = barcode.cursorPosition()
                barcode.setText(barcode_transfer)
                barcode.setText(old_text_input_barcode_edit)
                barcode.setCursorPosition(cursor_position)
                previous_focus_widget.setFocus()
            else:
                new_text = old_text_input_barcode_edit + input_value
                barcode.setText(new_text)
                cursor_position = len(new_text)
                barcode.setCursorPosition(cursor_position)
                barcode.setFocus()
        else:
            input_value = old_text_input_barcode_edit

        return input_value

    # Get product by barcode
    async def process_barcode(self, barcode_transfer=None, is_manual=None):
        input_value = self.prepare_barcode_input(barcode_transfer=barcode_transfer,is_manual=is_manual)

        if not input_value:
            return

        try:
            # with SessionLocal() as session:
            #     rep = ProductRepository(session)
            #     # self.number_check =
            #     product = rep.get_by_barcode(input_value)
            #
            #     print(product)

            product = self.db.get_product_by_barcode(input_value)

            if product:
                # product: (barcode, name, quantity, price, id)
                name = product[1]
                left_panel = self.main_window.left_panel
                left_panel.product_model.add_product(*product)
                self.update_total()
                left_panel.set_product_name(name)
                left_panel.table_view.viewport().update()
            else:
                self.main_window.left_panel.set_product_name("Товар не найден")
                # player = SoundPlayer()

            self.main_window.right_panel.barcode_edit.clear()
            self.focus_table()


        except Exception as a:
            print(a)

    # Seach on click key
    def get_list_product_on_keypress(self):
        try:
            update_results(db=self.db,input_field=self.main_window.right_panel.barcode_edit,
                list_result=self.main_window.right_panel.list_search_product, **POSITION_CONFIG.get("main")
            )
        except Exception as a:
            print(a)

    def select_item_for_search(self):
        select_current_item(
            list_result=self.main_window.right_panel.list_search_product,
            handler_function=self.main_window.event_handler.handle_barcode_detected,
            is_main=True,
        )

    @staticmethod
    def format_total(total: float) -> str:
        """Форматирует сумму: целые числа без дробной части, дробные — с двумя знаками."""
        return f"{total:.0f}" if total == int(total) else f"{total:.2f}"

    # Any function
    def update_total(self):
        """ Обновляет итоговую сумму и состояние кнопок. """
        self.total_sum = self.main_window.left_panel.product_model.get_total()
        self.main_window.left_panel.set_total(self.format_total(self.total_sum))
        self.update_buttons_state()
        if self.total_sum == 0:
            self.main_window.left_panel.set_product_name(self.name_)

    def delete_selected_product(self):
        """Удаляет выбранный товар из таблицы и пересчитывает итоговую сумму."""
        try:
            row = self.main_window.left_panel.product_model.get_selected_row()
            if row is not None:
                self.main_window.left_panel.product_model.remove_product_by_row(row)  # Удаляем строку из модели
                self.update_total()  # Пересчитываем сумму
                self.update_buttons_state()  # Обновляем состояние кнопок
                self.main_window.left_panel.table_view.setFocus()
        except Exception as e:
            print(f"Ошибка при удалении товара: {e}")

    def update_buttons_state(self):
        """ Обновляет состояние кнопок в зависимости от наличия товаров и выделенных строк. """
        has_items = self.main_window.left_panel.product_model.rowCount() > 0
        selected_rows = self.main_window.left_panel.table_view.selectionModel().selectedRows()
        has_selected = len(selected_rows) > 0

        # Оплата и Отмена активны, если есть хотя бы один товар в таблице
        self.main_window.left_panel.pay_button.setEnabled(has_items)
        self.main_window.left_panel.cancel_button.setEnabled(has_items)

        # Активна кнопка "Изменить кол-во" только при выборе одной строки.
        self.main_window.right_panel.edit_quantity_button.setEnabled(len(selected_rows) == 1)

        # Кнопка Удалить товар активна, если выбрана хотя бы одна строка
        self.main_window.right_panel.delete_button.setEnabled(has_selected)

    def clear_table(self):
        self.main_window.left_panel.product_model.clear()
        self.update_total()
        self.main_window.left_panel.set_product_name(self.name_)
        self.main_window.left_panel.table_view.setFocus()

    def update_check_number(self):
        with SessionLocal() as session:
            rep = SaleRepository(session)
            self.number_check = rep.get_next_sale_number()
        self.main_window.top_panel.set_check_number(self.number_check)