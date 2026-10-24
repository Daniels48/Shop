import asyncio
import time
import re

from PyQt5.QtCore import QObject, QEvent, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QMessageBox


ENGLISH_LETTERS = "abcdefghijklmnopqrstuvwxyz"
RUSSIAN_LETTERS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"

RAW_ALL_LETTERS = ENGLISH_LETTERS + RUSSIAN_LETTERS
LETTERS = re.sub(r"[tеdвкraфзpлklд]", "", RAW_ALL_LETTERS)


class EventHandler(QObject):
    barcode_detected = pyqtSignal(str, bool)  # Сигнал для передачи штрих-кода и флага ручного ввода

    def __init__(self, main_window, presenter):
        super().__init__(main_window)

        self.main_window = main_window
        self.presenter = presenter

        self.input_field = main_window.right_panel.barcode_edit
        self.table = main_window.left_panel.table_view

        self.input_buffer = ""
        self.last_time = time.time()
        self.max_time_between_keys = 0.2
        self.min_barcode_length = 8
        self.last_focused_widget = None
        # self.main_window.installEventFilter(self)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.check_input)

        self.input_buffer = ""
        self.last_time = 0
        self.max_time_between_keys = 0.2
        self.min_barcode_length = 8

    def install(self):
        # Фильтр для главного окна
        self.main_window.installEventFilter(self)

        # # Фильтр для основных виджетовё
        # self.main_window.left_panel.table_view.installEventFilter(self)
        # self.main_window.right_panel.barcode_edit.installEventFilter(self)
        # self.main_window.right_panel.list_search_product.installEventFilter(self)

    def handle_barcode_detected(self,barcode_transfer=None,is_manual=False):
        asyncio.create_task(self.presenter.process_barcode(barcode_transfer=barcode_transfer,is_manual=is_manual))

    def handle_product_selected(self, barcode):
        self.handle_barcode_detected(barcode_transfer=barcode,is_manual=True)

    def eventFilter(self, source, event):

        if event.type() == QEvent.WindowDeactivate:
            self.last_focused_widget = self.main_window.focusWidget()

        if event.type() == QEvent.WindowActivate:
            # Проверяем, не находится ли фокус на поле ввода
            if self.last_focused_widget:
                try:
                    QTimer.singleShot(100, lambda: self.last_focused_widget.setFocus())
                except Exception as a:
                    print(a)


        if isinstance(event, QKeyEvent):

            key = event.key()
            key_text = event.text()
            current_time = time.time()
            list_data = self.main_window.right_panel.list_search_product
            input_field = self.main_window.right_panel.barcode_edit


            # Если фокус на поле ввода штрих-кода
            if self.input_field.hasFocus() and key not in (Qt.Key_Up, Qt.Key_Down):

                if key == Qt.Key_Escape and event.type() == 6:
                    if self.main_window.right_panel.list_search_product.isVisible():
                        self.main_window.right_panel.list_search_product.setVisible(False)

                    self.main_window.right_panel.barcode_edit.setText("")
                    self.main_window.left_panel.table_view.setFocus()
                    return True
                else:
                    return False  # Не обрабатываем их в фильтре, передаем в поле ввода

            if key in (Qt.Key_Up, Qt.Key_Down):  # Стрелки вверх и вниз
                if event.type() == 6:
                    try:
                        if list_data.isVisible() and list_data.count() > 0:
                            current_row = list_data.currentRow()
                            if event.key() == Qt.Key_Down:  # Стрелка вниз
                                if current_row == -1:
                                    list_data.setCurrentRow(0)
                                    list_data.setFocus()


                            elif event.key() == Qt.Key_Up:  # Стрелка вверх
                                if current_row == 0:
                                    list_data.setCurrentRow(-1)
                                    input_field.setFocus()

                            return True
                    except Exception as a:
                        print(a)

                    if not self.table.hasFocus():  # Если таблица не в фокусе, ставим фокус
                        self.table.setFocus()


                    # Отправляем обработку стрелки в стандартный обработчик
                    return True

            elif key == Qt.Key_Return or key == Qt.Key_Enter:  # Обработка Enter (штрих-код)
                current_row = list_data.currentRow()
                if list_data.isVisible() and list_data.count() > 0 and current_row != -1:
                    try:
                        item = list_data.currentItem()
                        product_data = item.data(Qt.UserRole)
                        product = product_data["data"]
                        barcode = product[0]
                        self.main_window.event_handler.handle_barcode_detected(
                            barcode_transfer=barcode,
                            is_manual=True,
                        )
                        list_data.setVisible(False)  # Скрываем список
                        return True
                    except Exception as a:
                        print(a)

                if len(self.input_buffer) >= self.min_barcode_length and self.input_buffer.isdigit():
                    self.barcode_detected.emit(self.input_buffer, True)
                    self.input_buffer = ""  # Очищаем буфер
                    return True
                return True

            # Обработка чисел (0-9)
            elif event.text().isdigit():
                if current_time - self.last_time > self.max_time_between_keys:
                    self.input_buffer = ""

                self.input_buffer += key_text
                self.last_time = current_time

                self.timer.start(int(self.max_time_between_keys * 1000))

                # Цифра вводится через поле штрихкода
                if not self.input_field.hasFocus():
                    self.input_field.setFocus()
                    self.input_field.setText(self.input_field.text() + key_text)
                    self.input_field.setCursorPosition(len(self.input_field.text()))

                return True

            elif event.text() and event.type() == 6 and event.text() in LETTERS:
                if not self.main_window.right_panel.barcode_edit.hasFocus():
                    self.main_window.right_panel.barcode_edit.setText(event.text())
                    self.main_window.right_panel.barcode_edit.setFocus()

            elif key == Qt.Key_Escape and event.type() == 6:
                if self.main_window.right_panel.list_search_product.isVisible():
                    self.main_window.right_panel.list_search_product.setVisible(False)

                self.main_window.right_panel.barcode_edit.setText("")
                self.main_window.left_panel.table_view.setFocus()
                return True


            elif key == Qt.Key_Backspace:
                if list_data.isVisible() and list_data.count() > 0:
                    text = input_field.text()
                    try:
                        self.main_window.right_panel.barcode_edit.setText(text[0:len(text)])
                        self.main_window.right_panel.barcode_edit.setFocus()
                    except Exception as a:
                        print(a)

        if event.type() == QEvent.KeyPress:
            self.handle_key_press(event)

        return False

    def check_input(self):
        if 0 < len(self.input_buffer) < self.min_barcode_length:
            self.barcode_detected.emit(self.input_buffer, False)
            self.input_buffer = ""

    def handle_key_press(self, event):
        key = event.key()
        text = event.text().lower()

        main_window = self.main_window
        presenter = self.presenter
        left_panel = main_window.left_panel
        product_model = left_panel.product_model

        # Стрелки для перемещения по таблице
        if key in (Qt.Key_Up, Qt.Key_Down):
            total_rows = product_model.rowCount()

            if total_rows > 0:
                selected_row = product_model.get_selected_row()

                if selected_row is None:
                    new_row = 0 if key == Qt.Key_Down else total_rows - 1
                else:
                    step = 1 if key == Qt.Key_Down else -1
                    new_row = max(
                        0,
                        min(total_rows - 1, selected_row + step),
                    )

                product_model.select_row(new_row)
                left_panel.table_view.setFocus()

            return

        # Редактирование количества
        if key == Qt.Key_L or text in ("l", "д"):
            presenter.open_quantity_dialog()
            return

        # Escape
        if key == Qt.Key_Escape:
            if product_model._products:
                presenter.clear_table()
            else:
                reply = QMessageBox.question(
                    main_window,
                    "Подтверждение",
                    "Вы уверены, что хотите закрыть приложение?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )

                if reply == QMessageBox.Yes:
                    main_window.close()

            return

        # Оплата
        if text in ("з", "p"):
            presenter.open_payment_dialog()
            return

        # Печать штрихкода
        if text in ("л", "k"):
            try:
                presenter.open_barcode_print_dialog()
            except Exception as exc:
                print(f"Ошибка печати штрихкода: {exc}")
            return

        # Открытие карточки товара
        if text in ("a", "ф"):
            presenter.open_product_dialog()
            return

        # Ручная оплата
        if text in ("к", "r"):
            presenter.open_manual_payment_dialog()
            return

        # Удаление товара
        if key == Qt.Key_D or text in ("d", "в"):
            try:
                presenter.delete_selected_product()
            except Exception as exc:
                print(f"Ошибка при удалении: {exc}")
            return

        # Последнее действие с товаром
        if key == Qt.Key_T or text in ("t", "е"):
            presenter.open_last_action_dialog()




#
# from PyQt5.QtCore import QEvent, QObject, pyqtSignal, QTimer, Qt
# from PyQt5.QtGui import QKeyEvent
# import time
# import re
# english_letters = "abcdefghijklmnopqrstuvwxyz"
# russian_letters = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
#
#
#
# raw_all_letters = english_letters.lower() + russian_letters.lower()
#
# letters = re.sub(r'[tеdвкraфзpлklд]', '', raw_all_letters)
#
#
# class MyEventFilter(QObject):  # Наследуем от QObject
#     barcode_detected = pyqtSignal(str, bool)  # Сигнал для передачи штрих-кода и флага ручного ввода
#
#     def __init__(self, main_window, input_field, table):
#         super().__init__()  # Инициализация родительского класса
#         self.input_buffer = ""  # Буфер для ввода
#         self.last_time = time.time()  # Время последнего ввода
#         self.max_time_between_keys = 0.2  # Максимальное время между клавишами
#         self.min_barcode_length = 8  # Минимальная длина штрих-кода
#         self.timer = QTimer(self)  # Таймер для отслеживания времени
#         self.timer.setSingleShot(True)
#         self.timer.timeout.connect(self.check_input)
#         self.input_field = input_field
#         self.table = table
#         self.main_window = main_window
#         self.main_window.installEventFilter(self)
#         self.last_focused_widget = None
#
#
#
#     def eventFilter(self, source, event):
#
#         if event.type() == QEvent.WindowDeactivate:
#             self.last_focused_widget = self.main_window.focusWidget()
#
#         if event.type() == QEvent.WindowActivate:
#             # Проверяем, не находится ли фокус на поле ввода
#             if self.last_focused_widget:
#                 try:
#                     QTimer.singleShot(100, lambda: self.last_focused_widget.setFocus())
#                 except Exception as a:
#                     print(a)
#
#
#         if isinstance(event, QKeyEvent):
#
#             key = event.key()
#             key_text = event.text()
#             current_time = time.time()
#             list_data = self.main_window.right_panel.list_search_product
#             input_field = self.main_window.right_panel.barcode_edit
#
#
#             # Если фокус на поле ввода штрих-кода
#             if self.input_field.hasFocus() and key not in ((Qt.Key_Up, Qt.Key_Down)):
#
#                 if key == Qt.Key_Escape and event.type() == 6:
#                     if self.main_window.right_panel.list_search_product.isVisible():
#                         self.main_window.right_panel.list_search_product.setVisible(False)
#
#                     self.main_window.right_panel.barcode_edit.setText("")
#                     self.main_window.left_panel.table_view.setFocus()
#                     return True
#                 else:
#                     return False  # Не обрабатываем их в фильтре, передаем в поле ввода
#
#             if key in (Qt.Key_Up, Qt.Key_Down):  # Стрелки вверх и вниз
#                 if event.type() == 6:
#                     try:
#                         if list_data.isVisible() and list_data.count() > 0:
#                             current_row = list_data.currentRow()
#                             if event.key() == Qt.Key_Down:  # Стрелка вниз
#                                 if current_row == -1:
#                                     list_data.setCurrentRow(0)
#                                     list_data.setFocus()
#
#
#                             elif event.key() == Qt.Key_Up:  # Стрелка вверх
#                                 if current_row == 0:
#                                     list_data.setCurrentRow(-1)
#                                     input_field.setFocus()
#
#                             return True
#                     except Exception as a:
#                         print(a)
#
#                     if not self.table.hasFocus():  # Если таблица не в фокусе, ставим фокус
#                         self.table.setFocus()
#
#
#                     # Отправляем обработку стрелки в стандартный обработчик
#                     return True
#
#             elif key == Qt.Key_Return or key == Qt.Key_Enter:  # Обработка Enter (штрих-код)
#                 current_row = list_data.currentRow()
#                 if list_data.isVisible() and list_data.count() > 0 and current_row != -1:
#                     try:
#                         item = list_data.currentItem()
#                         product_data = item.data(Qt.UserRole)
#                         product = product_data["data"]
#                         barcode = product[0]
#                         self.main_window.event_handler.handle_barcode_detected(
#                             barcode_transfer=barcode,
#                             is_manual=True,
#                         )
#                         list_data.setVisible(False)  # Скрываем список
#                         return True
#                     except Exception as a:
#                         print(a)
#
#                 if len(self.input_buffer) >= self.min_barcode_length and self.input_buffer.isdigit():
#                     self.barcode_detected.emit(self.input_buffer, True)
#                     self.input_buffer = ""  # Очищаем буфер
#                     return True
#                 return True
#
#             # Обработка чисел (0-9)
#             elif event.text().isdigit() and event.type() == 6:
#                 if current_time - self.last_time > self.max_time_between_keys:
#                     self.input_buffer = ""
#                     self.timer.start(int(self.max_time_between_keys * 1000))
#
#                 self.input_buffer += key_text
#                 self.last_time = current_time
#                 return True
#
#             elif event.text() and event.type() == 6 and event.text() in letters:
#                 if not self.main_window.right_panel.barcode_edit.hasFocus():
#                     self.main_window.right_panel.barcode_edit.setText(event.text())
#                     self.main_window.right_panel.barcode_edit.setFocus()
#
#             elif key == Qt.Key_Escape and event.type() == 6:
#                 if self.main_window.right_panel.list_search_product.isVisible():
#                     self.main_window.right_panel.list_search_product.setVisible(False)
#
#                 self.main_window.right_panel.barcode_edit.setText("")
#                 self.main_window.left_panel.table_view.setFocus()
#                 return True
#
#
#             elif key == Qt.Key_Backspace:
#                 if list_data.isVisible() and list_data.count() > 0:
#                     text = input_field.text()
#                     try:
#                         self.main_window.right_panel.barcode_edit.setText(text[0:len(text)])
#                         self.main_window.right_panel.barcode_edit.setFocus()
#                     except Exception as a:
#                         print(a)
#
#
#         return False
#
#     def check_input(self):
#         if len(self.input_buffer) > 0 and len(self.input_buffer) < self.min_barcode_length:
#             self.barcode_detected.emit(self.input_buffer, False)
#             self.input_buffer = ""