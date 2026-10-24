import usb.core
import usb.util
import time
from random import randint
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QWidget, QLabel, QStackedWidget, QHBoxLayout,
    QSizePolicy, QMessageBox, QLineEdit, QListWidget,QListWidgetItem
)
from PyQt5.QtCore import Qt, QTimer
from view.dialog.product_history.utils import format_decimal_to_str

from search_global import create_search_result_list, update_results, POSITION_CONFIG, select_current_item, get_product_and_handle



id_vendor_xPrinter = 0x1FC9
id_product_xPrinter = 0x2016

class PrintDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Печать штрих-кодов")
        self.setFixedSize(1000, 700)


        self.check_valid_printer()

        # Основной layout
        self.layout = QVBoxLayout(self)

        # Создаем QStackedWidget для переключения страниц
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Главное меню
        self.main_menu = QWidget()
        self.layout_main_menu = self.create_main_menu()
        self.main_menu.setLayout(self.layout_main_menu)
        self.stacked_widget.addWidget(self.main_menu)

        # Страницы для печати
        self.page_one = self.create_one_print_page()
        self.page_multiple = self.create_multiple_page()

        self.stacked_widget.addWidget(self.page_one)
        self.stacked_widget.addWidget(self.page_multiple)

        # Устанавливаем начальную страницу (главное меню)
        self.stacked_widget.setCurrentWidget(self.main_menu)


    def create_main_menu(self):
        """Создает главное меню с двумя кнопками"""

        def set_style_btn(btn):
            btn.setStyleSheet("height:60px; font-size: 28px; border-radius:10px; border: 1px solid #999999;")  # Можно добавить кастомные стили
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Растягиваем по ширине

        main_layout = QVBoxLayout()

        text = QLabel("Печать штрих-кодов:")
        text.setAlignment(Qt.AlignCenter)
        text.setStyleSheet("font-size: 32px; font-weight: bold;")

        main_layout.addWidget(text)

        layout_btn = QHBoxLayout()

        # Создание кнопок
        btn_one = QPushButton("Один штрих-код")
        btn_multiple = QPushButton("Множество штрих-кодов")

        # Применяем одинаковые стили для кнопок
        set_style_btn(btn_one)
        set_style_btn(btn_multiple)

        # Подключаем кнопки к действиям
        btn_one.clicked.connect(lambda: self.switch_page(self.page_one))
        btn_multiple.clicked.connect(lambda: self.switch_page(self.page_multiple))

        # Добавляем кнопки в layout
        layout_btn.addWidget(btn_one)
        layout_btn.addWidget(btn_multiple)

        # Устанавливаем одинаковую ширину для обеих кнопок
        layout_btn.setStretch(0, 1)  # Кнопка 1
        layout_btn.setStretch(1, 1)  # Кнопка 2

        main_layout.addLayout(layout_btn)

        return main_layout

    def switch_page(self, page):
        first_page = True if page is self.page_one else False
        self.stacked_widget.setCurrentWidget(page)
        if first_page:
            self.search_barcode_edit_print_one.setFocus()
        else:
            self.text_edit_multiple_print.setFocus()

    # ----------------------------------First page------------------------------------
    def create_one_print_page(self):
        """Создает страницу для печати одного штрих-кода'"""
        page = QWidget()
        layout = QVBoxLayout(page)

        def create_search_layot():
            layot = QHBoxLayout()
            search_button = QPushButton("🔍 Поиск")
            search_button.setStyleSheet("width: 85px; height: 40px; background-color: #24ACF2; font-size:14px; border-radius: 5px;")
            self.search_barcode_edit_print_one = QLineEdit()
            self.search_barcode_edit_print_one.setStyleSheet("height:40px; border-radius:10px; border: 2px solid #24ACF2; font-size: 24px;padding-left:5px;")
            self.search_barcode_edit_print_one.setPlaceholderText("Введите название или штрих-код товара ...")
            self.search_barcode_edit_print_one.textChanged.connect(self.update_result_one_print)

            self.search_barcode_edit_print_one.returnPressed.connect(self.entered_button_search_one_print)
            search_button.clicked.connect(self.entered_button_search_one_print)

            layot.addWidget(self.search_barcode_edit_print_one)
            layot.addWidget(search_button)
            return layot

        def create_bottom_btn():
            layout = QHBoxLayout()
            self.print_button_one = QPushButton("🖨️ Печать")
            back_button = QPushButton("⬅️ Назад")
            self.set_btn_style(self.print_button_one,True)
            self.set_btn_style(back_button)
            back_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.main_menu))
            self.print_button_one.clicked.connect(self.print_one)
            layout.addWidget(self.print_button_one)
            layout.addWidget(back_button)
            return layout

        def create_text_edit(placeholdertext):
            back_color = "" if placeholdertext else "background-color: #D6DADF; color:black;"
            text_edit = QLineEdit()
            text_edit.setStyleSheet(
                f"height:40px; border-radius:10px; border: 1px solid black; font-size: 24px;padding-left:5px;{back_color}margin-bottom:10px;")
            text_edit.setPlaceholderText(placeholdertext)
            return text_edit

        def create_label(name):
            label = QLabel(name)
            label.setStyleSheet("font-size:20px;color:black;")
            return label


        label = create_label("Штрих-код:")
        label_0 = create_label("Информация о товаре:")

        search_layout = create_search_layot()
        self.text_edit_one_print = create_text_edit("Введите штрих-код для печати ...")
        self.name_edit_one_print = create_text_edit("")
        self.name_edit_one_print.setEnabled(False)
        bottom_btn = create_bottom_btn()

        self.list_one_print_search = create_search_result_list(self, self.search_barcode_edit_print_one)
        self.list_one_print_search.itemClicked.connect(self.select_current_item_one_print)

        layout.addLayout(search_layout)
        layout.addStretch(1)
        layout.addWidget(label_0)
        layout.addWidget(self.name_edit_one_print)
        layout.addWidget(label)
        layout.addWidget(self.text_edit_one_print)
        layout.addStretch(1)
        layout.addLayout(bottom_btn)
        layout.setAlignment(Qt.AlignCenter)  # Разница с PyQt6

        return page

    def update_result_one_print(self):
        update_results(self.db, self.search_barcode_edit_print_one, self.list_one_print_search, **POSITION_CONFIG.get("print"))

    def select_current_item_one_print(self):
        select_current_item(self.list_one_print_search, self.entered_button_search_one_print)

    def entered_button_search_one_print(self, product_value=False):
        get_product_and_handle(product_value, self.search_barcode_edit_print_one, self.db, self.succes_print)

    def succes_print(self, product):
        self.text_edit_one_print.setText(product[0])
        self.search_barcode_edit_print_one.setText("")
        name = product[1]
        price = f"{format_decimal_to_str(product[3])} ₽"
        count = f"{format_decimal_to_str(product[2])} шт. (кг.)"
        text = f"{name}; {price}; {count}"
        self.name_edit_one_print.setText(text)

    def set_btn_style(self, btn, is_print=False, is_disable=False):
        style = ": #D6DADF" if is_disable else "#6EC6F2" if is_print else "white"
        btn.setStyleSheet(
            f"height: 60px; border-radius:10px; border: 1px solid #999999; font-size:32px; background-color: {style};")
        btn.setEnabled(not is_disable)

    def print_one(self):
        self.set_btn_style(self.print_button_one, True, True)
        barcode = self.text_edit_one_print.text().strip()

        if not barcode:
            QMessageBox.warning(self, "Ошибка", f"Заполните поле штрих-кода")
            self.set_btn_style(self.print_button_one, True, False)
            return
        status = self.get_printer_status()
        is_ready_printer = status[0]
        if is_ready_printer:
            barcode = barcode.split(";")[0]
            if len(barcode) != 13:
                QMessageBox.warning(self, "Ошибка", "Штрих-код неправильного формата!")
                return
            self.print_ean13(barcode)
            self.text_edit_one_print.setText("")
            self.name_edit_one_print.setText("")
            QMessageBox.information(self, "Успех", f"Штрих-код {barcode} успешно напечатан!")
            self.set_btn_style(self.print_button_one, True, False)
        else:
            QMessageBox.warning(self, "Ошибка", status[1])
            self.set_btn_style(self.print_button_one, True, False)



    # ----------------------------------Multiple page--------------------------------
    def create_multiple_page(self):
        """Создает страницу для печати одного штрих-кода'"""
        page = QWidget()
        layout = QVBoxLayout(page)

        def create_bottom_btn():
            layout = QHBoxLayout()
            self.print_button_multiple = QPushButton("🖨️ Печать")
            back_button = QPushButton("⬅️ Назад")
            self.set_btn_style(self.print_button_multiple, True)
            self.set_btn_style(back_button)
            back_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.main_menu))
            self.print_button_multiple.clicked.connect(self.print_multiple_barcodes)
            layout.addWidget(self.print_button_multiple)
            layout.addWidget(back_button)
            return layout

        def create_text_edit(placeholdertext):
            back_color = "" if placeholdertext else "background-color: #D6DADF; color:black;"
            text_edit = QLineEdit()
            text_edit.setStyleSheet(
                f"height:40px; border-radius:10px; border: 1px solid black; font-size: 24px;padding-left:5px;{back_color}margin-bottom:10px;")
            text_edit.setPlaceholderText(placeholdertext)
            return text_edit

        def create_label(name):
            label = QLabel(name)
            label.setStyleSheet("font-size:20px;color:black;")
            return label

        label = create_label("Колличество штрих-кодов:")

        self.text_edit_multiple_print = create_text_edit("Введите количество штрих-кодов для печати ...")
        self.text_edit_multiple_print.setValidator(QIntValidator(0, 99))

        bottom_btn = create_bottom_btn()
        layout.addStretch(1)
        layout.addWidget(label)
        layout.addWidget(self.text_edit_multiple_print)
        layout.addStretch(1)
        layout.addLayout(bottom_btn)
        layout.setAlignment(Qt.AlignCenter)  # Разница с PyQt6

        return page

    def print_multiple_barcodes(self):
        self.set_btn_style(self.print_button_multiple, True, True)
        self.check_valid_printer()
        input_value = int(self.text_edit_multiple_print.text().strip())
        list_barcodes = self.get_random_count_barcodes(input_value)

        # status = self.get_printer_status()
        # is_ready_printer = status[0]
        # if is_ready_printer:
        #     self.print_ean13(barcode)
        #     self.text_edit_one_print.setText("")
        #     self.name_edit_one_print.setText("")
        #     QMessageBox.information(self, "Успех", f"Штрих-код {barcode} успешно напечатан!")
        #     self.set_btn_style(self.print_button_one, True, False)
        # else:
        #     QMessageBox.warning(self, "Ошибка", status[1])
        #     self.set_btn_style(self.print_button_one, True, False)


        max_wait_time = 10  # Максимальное время ожидания в секундах
        start_time = time.time()  # Начальное время отсчёта

        for barcode in list_barcodes:
            while not self.get_printer_status()[0]:  # Проверяем статус принтера
                elapsed_time = time.time() - start_time
                if elapsed_time > max_wait_time:
                    status = self.get_printer_status()
                    is_ready = status[0]
                    text = status[1]
                    if not is_ready:
                        QMessageBox.warning(self, "Ошибка", text)
                        return  # Выход из функции
                    else:
                        QMessageBox.warning(self, "Ошибка", "Принтер недоступен слишком долго. Прерываем печать.")
                        return
                time.sleep(1)  # Ожидание перед повторной проверкой

            # Печатаем штрих-код
            self.print_ean13(barcode)

            # Сбрасываем таймер после успешной печати
            start_time = time.time()  # Сброс таймера после успешной печати

        QMessageBox.information(self, "Успех", f"{input_value} штрих-кодов успешно напечатаны!")
        self.set_btn_style(self.print_button_multiple, True, False)
        self.text_edit_multiple_print.setText("")
        self.text_edit_multiple_print.setFocus()


    def get_random_count_barcodes (self, count_barcodes):
        list_barcodes = self.db.get_all_barcodes()
        new_list = []
        while len(new_list) != count_barcodes:
            new_barcode = "".join([str(randint(1, 9)) for i in range(13)])
            if new_barcode not in list_barcodes:
                new_barcode = "".join([str(randint(1, 9)) for i in range(13)])
            new_list.append(new_barcode)
        return new_list
    # -----------------------------------------------------------------------------

    # ------------------------------------Print methods----------------------------
    def print_ean13(self, barcode_number, idVendor=id_vendor_xPrinter, idProduct=id_product_xPrinter):
        try:
            # Найти принтер
            printer = usb.core.find(idVendor=idVendor, idProduct=idProduct)
            if printer is None:
                self.check_valid_printer()

            printer.set_configuration()

            # Найти Bulk OUT endpoint (0x01)
            cfg = printer.get_active_configuration()
            intf = cfg[(0, 0)]
            ep_out = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
            )

            if ep_out is None:
                raise ValueError("Не найден endpoint для отправки данных")

            commands = f"""
                    SIZE 30 mm, 20 mm
                    GAP 1 mm, 0
                    CLS
                    BARCODE 10,65,"EAN13",50,1,0,2,2,"{barcode_number}"
                    PRINT 1,1
                    """

            # Отправка команд в принтер
            ep_out.write(commands.encode('utf-8'))  # Используем UTF-8 вместо ASCII для большей совместимости
            print(f"✅ Штрих-код {barcode_number} отправлен на печать")

        except Exception as e:
            print("❌ Ошибка при печати:", e)

    def get_printer_status(self):
        """Запрашивает статус принтера и возвращает его состояние в виде строки."""
        try:
            # Найти принтер
            printer = usb.core.find(idVendor=id_vendor_xPrinter, idProduct=id_product_xPrinter)
            if printer is None:
                return "❌ Принтер не найден"

            # Получаем активную конфигурацию
            cfg = printer.get_active_configuration()
            intf = cfg[(0, 0)]

            # Ищем IN-эндпоинт для чтения статуса
            ep_in = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
            )

            if ep_in is None:
                return "❌ Не найден endpoint для чтения статуса"

            # Читаем статус
            print(f"✅ Читаем статус с endpoint {ep_in.bEndpointAddress}...")
            status_bytes = printer.read(ep_in.bEndpointAddress, ep_in.wMaxPacketSize, timeout=1000)
            print(f"🔍 Статус принтера (сырые данные): {status_bytes}")

            # Расшифровываем статус
            return self.parse_printer_status(status_bytes)

        except usb.core.USBError as e:
            return f"⚠ Ошибка при получении статуса: {e}"
        except Exception as e:
            return f"❌ Неизвестная ошибка: {e}"

    def parse_printer_status(self, status_bytes):
        """Расшифровывает полученный статус принтера."""
        if len(status_bytes) < 2:
            return "❌ Ошибка: некорректный статус"

        byte1, byte2 = status_bytes[0], status_bytes[1]

        # Разбираем первый байт
        printer_ready = bool(byte1 & 0b01000000)  # Принтер включен
        paper_out = bool(byte1 & 0b00010000)  # Нет бумаги

        # Разбираем второй байт
        printer_busy = bool(byte2 & 0b01000000)  # Принтер занят (печатает)
        near_paper_end = bool(byte2 & 0b00010000)  # Бумага почти закончилась
        has_error = bool(byte2 & 0b00100000)  # Ошибка принтера

        # Определяем общий статус
        if paper_out:
            return False, "❌ Ошибка: Нет бумаги"
        elif has_error:
            return False, "❌ Ошибка принтера"
        elif printer_busy:
            return False, "⏳ Принтер печатает"
        elif near_paper_end:
            return True, "⚠ Бумага почти закончилась"
        elif printer_ready:
            return True, "✅ Принтер готов"
        else:
            return False, "⚠ Неизвестный статус"

    def check_valid_printer(self):
        printer = usb.core.find(idVendor=id_vendor_xPrinter, idProduct=id_product_xPrinter)
        if printer is None:
            QMessageBox.warning(self, "Ошибка", "Принтер не подключен или не найден.", QMessageBox.Ok)
            QTimer.singleShot(0, self.reject)  # Отложенный вызов reject
    # ----------------------------------------------------------------------------

    def calculate_ean13_checksum(self, barcode):
        """
        Функция для вычисления контрольной суммы для EAN-13.

        :param barcode: Строка из 12 цифр (без контрольной суммы)
        :return: Контрольная сумма (13-я цифра)
        """
        if len(barcode) != 12 or not barcode.isdigit():
            raise ValueError("Входные данные должны быть строкой из 12 цифр")

        total = 0

        # Проходим по всем цифрам
        for i, digit in enumerate(barcode):
            digit = int(digit)
            # На нечетных позициях (по индексации начиная с 0) ставим вес 1, на четных - вес 3
            if i % 2 == 0:  # Нечетные позиции (по индексации с 0)
                total += digit
            else:  # Четные позиции
                total += digit * 3

        # Вычисляем остаток от деления на 10
        remainder = total % 10
        # Контрольная сумма = 10 - остаток, если остаток не равен 0, иначе контрольная сумма 0
        checksum = 0 if remainder == 0 else 10 - remainder

        return checksum
