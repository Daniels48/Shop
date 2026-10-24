from PyQt5.QtWidgets import QMessageBox
from view.dialog.product_history.utils import format_decimal_to_str


class Product:
    """Класс для представления продукта."""
    def __init__(self, barcode, name, price, quantity, id, main_window):
        self.barcode = barcode
        self.name = name
        self.quantity = quantity
        self.price = price
        self.id = id
        self.main_window = main_window
        self.error = False
        self.current_quantity = self.set_quantity(1)
        self.total = round(float(self.current_quantity) * float(price),2)


    def update_quantity(self, quantity):
        """Обновить количество продукта."""

        new_quantity = self.current_quantity + quantity

        if new_quantity > self.quantity:
            QMessageBox.warning(self.main_window, "Ошибка", self.get_text_warning(), QMessageBox.Ok)
            self.current_quantity = self.quantity
            self.update_total()
            return
        if new_quantity == 0:
            self.current_quantity = 1
            self.update_total()
            return
        else:
            self.current_quantity = new_quantity
            self.update_total()


    def set_quantity(self, new_quantity):
        if new_quantity > self.quantity:
            if self.quantity <= 0:
                QMessageBox.warning(self.main_window, "Ошибка", "Данный товар закончился на складе!", QMessageBox.Ok)
                self.error = True
                return 1
            QMessageBox.warning(self.main_window, "Ошибка", self.get_text_warning(), QMessageBox.Ok)
            self.current_quantity = self.quantity


        else:
            self.current_quantity = new_quantity
        self.update_total()

        return self.current_quantity

    def update_total(self):
        self.total = round(float(self.current_quantity) * float(self.price),2)

    def get_text_warning(self):
        header_text = "Добавляемое значение превышает колличество на складе!"
        bottom_text = f"Колличество на складе {format_decimal_to_str(self.quantity)} шт.(кг.)"
        name = f"{self.name}"
        return f"{header_text}\n\n{name}\n\n{bottom_text}"

