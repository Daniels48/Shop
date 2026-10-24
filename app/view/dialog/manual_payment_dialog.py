from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel,  QWidget, QLineEdit, QHBoxLayout,  QMessageBox, QStackedWidget,
)
from PyQt5.QtGui import  QDoubleValidator, QIcon
from PyQt5.QtCore import Qt, QSize
from app.utils.get_path import get_resourse_path_icon
from app.utils.payment_utils import PaymentThread, check_valid_terminal


class PayDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Оплата без штрих-кода")
        self.setFixedSize(800, 400)
        self.confirmed = False  # Флаг подтверждения оплаты
        self.abort_file_created = False
        self.pay_value = 0
        self.payment_method = None

        # Основной вертикальный layout
        self.layout = QVBoxLayout()
        self.initUI()
        self.setLayout(self.layout)
        self.stacked_widget.setCurrentIndex(0)

    def initUI(self):
        self.stacked_widget = QStackedWidget()

        def create_layout_input_page():
            layout = QVBoxLayout()
            self.text_field = QLabel("Оплата без штрих-кода")
            self.text_field.setStyleSheet("font-size:48px;padding-top:40px;")
            layout.addWidget(self.text_field, alignment=Qt.AlignHCenter)

            # Поле ввода
            self.input_field = QLineEdit(self)
            validator = QDoubleValidator(0, 999999, 2)
            validator.setNotation(QDoubleValidator.StandardNotation)
            self.input_field.setValidator(validator)
            self.input_field.setStyleSheet("height: 50px; font-size:38px;border-radius:15px;"
                                           "padding-left:5px;border:1px solid black;")
            self.input_field.setPlaceholderText("Введите сумму ...")

            layout.addStretch(1)
            layout.addWidget(self.input_field)
            layout.addStretch(1)

            # Кнопки
            button_layout = QHBoxLayout()

            # Кнопка запятой
            comma_button = QPushButton("Запятая [,]")
            comma_button.setStyleSheet(
                "height:50px; font-size:30px; border-radius:10px; background-color:#D3D3D3;")
            comma_button.clicked.connect(self.insert_comma)
            button_layout.addWidget(comma_button)

            # Кнопка подтверждения
            self.confirm_button = QPushButton("Продолжить")
            self.confirm_button.setStyleSheet("height:50px; font-size:30px;color:white;"
                                              "border-radius:10px;background-color:#01B4E4;")
            self.confirm_button.clicked.connect(self.on_confirm)
            button_layout.addWidget(self.confirm_button)

            layout.addLayout(button_layout)
            # self.setLayout(self.layout_card)
            return layout

        def create_layout_choose_methods_pay():
            def create_button_methods_pay():
                # Горизонтальный layout для кнопок
                buttons_layout = QHBoxLayout()
                # Кнопки выбора метода оплаты
                self.cash_button = QPushButton("Наличные")
                self.card_button = QPushButton("Карта")

                # Текущий выбранный индекс (0 - "Наличные", 1 - "Карта")
                self.selected_index = 0
                # Подключаем обработку событий
                self.setFocusPolicy(Qt.StrongFocus)

                icon_cash_path = get_resourse_path_icon("1.ico")
                icon_card_path = get_resourse_path_icon("credit2.ico")

                # Добавляем иконки
                self.cash_button.setIcon(QIcon(icon_cash_path))  # Укажите правильный путь
                self.card_button.setIcon(QIcon(icon_card_path))

                # Задаем размер иконок
                self.cash_button.setIconSize(QSize(55, 55))
                self.card_button.setIconSize(QSize(70, 70))

                self.setButtonStyle(self.card_button)
                self.setButtonStyle(self.cash_button, True)

                self.cash_button.clicked.connect(self.accept_cash)
                self.card_button.clicked.connect(self.accept_card)

                buttons_layout.addWidget(self.cash_button)
                buttons_layout.addWidget(self.card_button)

                return buttons_layout

            def create_text_pay():
                amount_layout = QHBoxLayout()
                amount_layout.setAlignment(Qt.AlignCenter)  # Выравниваем весь layout по центру

                # Текст "К оплате:"
                amount_label = QLabel("К оплате:")
                amount_label.setStyleSheet("font-size:50px; color:#999999;")
                amount_label.setAlignment(Qt.AlignCenter)

                # Блок с суммой и валютой
                amount_layout_value = QHBoxLayout()
                amount_layout_value.setAlignment(Qt.AlignCenter)

                self.amount_label_value = QLabel(f"{self.pay_value}")
                self.amount_label_value.setStyleSheet("font-size:52px; color:#3D3D3D;margin-bottom:1px; "
                                                      "margin-left:10px;border-bottom: 3px solid #01B4E4;")
                self.amount_label_value.setAlignment(Qt.AlignCenter)

                amount_label_valute = QLabel("₽")
                amount_label_valute.setStyleSheet(
                    "font-size:54px; font-weight:500; color:#0A0A0A;padding-bottom:5px;")
                amount_label_valute.setAlignment(Qt.AlignCenter)

                # Добавляем сумму и знак валюты в общий блок
                amount_layout_value.addWidget(self.amount_label_value)
                amount_layout_value.addWidget(amount_label_valute)

                # Добавляем элементы в основной горизонтальный layout
                amount_layout.addStretch(1)  # Отступ слева для центрирования
                amount_layout.addWidget(amount_label)
                amount_layout.addSpacing(10)  # Маленький отступ между текстом и суммой
                amount_layout.addLayout(amount_layout_value)
                amount_layout.addStretch(1)  # Отступ справа для центрирования
                return amount_layout

            layout = QVBoxLayout()
            layout.addStretch(1)

            layout_amount_to_pay = create_text_pay()
            layout_buttonn_methods_pay = create_button_methods_pay()

            layout.addLayout(layout_amount_to_pay)
            layout.addStretch(1)
            layout.addLayout(layout_buttonn_methods_pay)
            return layout

        def create_layout_cash_page1():
            """Переключение интерфейса в режим ввода полученной суммы"""
            layout = QVBoxLayout()

            self.payment_label_cash = QLabel(f"К оплате: {self.pay_value} ₽")
            self.payment_label_cash.setStyleSheet("font-size:38px;padding-top:40px;")
            layout.addWidget(self.payment_label_cash, alignment=Qt.AlignHCenter)

            # Поле ввода
            self.input_field_cash1 = QLineEdit(self)
            validator = QDoubleValidator(0, 999999, 2)
            validator.setNotation(QDoubleValidator.StandardNotation)
            self.input_field_cash1.setValidator(validator)
            self.input_field_cash1.setStyleSheet("height: 50px; font-size:38px;border-radius:15px;"
                                                 "padding-left:5px;border:1px solid black;")
            self.input_field_cash1.setPlaceholderText("Введите полученную сумму ...")

            layout.addStretch(1)
            layout.addWidget(self.input_field_cash1)
            layout.addStretch(1)

            # Кнопки
            button_layout = QHBoxLayout()

            self.back_button_cash1 = QPushButton("Назад", self)
            self.back_button_cash1.setStyleSheet("height:50px; font-size:30px;color:white;"
                                                 "border-radius:10px;background-color:#FF5555;")
            # Кнопка подтверждения
            self.confirm_button_cash1 = QPushButton("Продолжить")
            self.confirm_button_cash1.setStyleSheet("height:50px; font-size:30px;color:white;"
                                                    "border-radius:10px;background-color:#01B4E4;")
            self.confirm_button_cash1.clicked.connect(self.accept_cash_finnaly_list)
            self.back_button_cash1.clicked.connect(self.back_cash)

            button_layout.addWidget(self.back_button_cash1)
            button_layout.addWidget(self.confirm_button_cash1)

            layout.addLayout(button_layout)
            return layout

        def create_layout_cash_page2():
            """Переключение интерфейса в режим ввода полученной суммы"""
            layout = QVBoxLayout()

            self.payment_label_cash_in = QLabel(f"Получено: {self.pay_value} ₽")
            self.payment_label_cash_in.setStyleSheet("font-size:38px;padding-top:30px;")
            layout.addWidget(self.payment_label_cash_in, alignment=Qt.AlignHCenter)

            self.payment_label_cash2 = QLabel(f"К оплате: {self.pay_value} ₽")
            self.payment_label_cash2.setStyleSheet("font-size:38px;padding-top:15px;")
            layout.addWidget(self.payment_label_cash2, alignment=Qt.AlignHCenter)

            self.payment_label_cash_out = QLabel(f"Сдача: {self.pay_value} ₽")
            self.payment_label_cash_out.setStyleSheet(
                "font-size:40px;padding-top:15px; padding-bottom: 30px;font-weight:700;")
            layout.addWidget(self.payment_label_cash_out, alignment=Qt.AlignHCenter)

            # Кнопки
            button_layout = QHBoxLayout()

            self.back_button_cash2 = QPushButton("Назад", self)
            self.back_button_cash2.setStyleSheet("height:50px; font-size:30px;color:white;"
                                                 "border-radius:10px;background-color:#FF5555;")
            # Кнопка подтверждения
            self.confirm_button_cash2 = QPushButton("Завершить")
            self.confirm_button_cash2.setStyleSheet("height:50px; font-size:30px;color:white;"
                                                    "border-radius:10px;background-color:#01B4E4;")
            self.confirm_button_cash2.clicked.connect(self.ok_valid)
            self.back_button_cash2.clicked.connect(self.back_cash)

            button_layout.addWidget(self.back_button_cash2)
            button_layout.addWidget(self.confirm_button_cash2)

            layout.addLayout(button_layout)
            return layout

        def create_layout_card_page():
            """Переключение интерфейса в режим ожидания оплаты"""
            layout = QVBoxLayout()
            text_field = QLabel("Касса ждёт оплаты ...")
            text_field.setStyleSheet("font-size:48px;padding-top:40px;")
            layout.addWidget(text_field, alignment=Qt.AlignHCenter)

            self.payment_label = QLabel(f"К оплате: {self.pay_value} ₽")
            self.payment_label.setStyleSheet("font-size:38px;padding-top:20px;")
            layout.addWidget(self.payment_label, alignment=Qt.AlignHCenter)

            self.cancel_button_pay = QPushButton("Отмена", self)
            self.cancel_button_pay.setStyleSheet(
                "height:50px; font-size:30px;color:white;border-radius:10px;background-color:#FF5555;")

            self.cancel_button_pay.clicked.connect(self.on_cancel)

            layout.addWidget(self.cancel_button_pay, alignment=Qt.AlignBottom)
            return layout

        # First (0)
        self.input_page = QWidget()
        self.layout_input_page = create_layout_input_page()
        self.input_page.setLayout(self.layout_input_page)
        self.stacked_widget.addWidget(self.input_page)

        # Second (1)
        self.choose_methods_pay_page = QWidget()
        self.layout_choose_methods_pay = create_layout_choose_methods_pay()
        self.choose_methods_pay_page.setLayout(self.layout_choose_methods_pay)
        self.stacked_widget.addWidget(self.choose_methods_pay_page)

        # Third (2)
        self.card_page = QWidget()
        self.card_layout_page = create_layout_card_page()
        self.card_page.setLayout(self.card_layout_page)
        self.stacked_widget.addWidget(self.card_page)

        # Four (3)
        self.cash_page1 = QWidget()
        self.layout_page1 = create_layout_cash_page1()
        self.cash_page1.setLayout(self.layout_page1)
        self.stacked_widget.addWidget(self.cash_page1)

        # Five (4)
        self.cash_page2 = QWidget()
        self.layout_page2 = create_layout_cash_page2()
        self.cash_page2.setLayout(self.layout_page2)
        self.stacked_widget.addWidget(self.cash_page2)

        self.layout.addWidget(self.stacked_widget)

    # First buttons
    def on_confirm(self):
        """Обработка нажатия кнопки 'Подтвердить'"""
        if self.check_input_value(self.input_field):
            value = self.get_value()
            self.pay_value = value

            self.amount_label_value.setText(self.pay_value)
            text = f"К оплате: {self.pay_value} ₽"

            self.payment_label_cash.setText(text)
            self.payment_label_cash2.setText(text)
            self.payment_label.setText(text)

            self.stacked_widget.setCurrentIndex(1)
            self.choose_methods_pay_page.setFocus()

    def insert_comma(self):
        """Добавляет запятую в поле ввода"""
        current_text = self.input_field.text()
        if "," not in current_text:
            self.input_field.setText(current_text + ",")
        self.input_field.setFocus()

    # ------------------------------------------------------------

    # Second buttons
    def accept_card(self):
        if check_valid_terminal(self):
            if not self.confirmed:  # Если это первое нажатие
                self.payment_method = "card_nobarcode"
                self.confirmed = True
                self.stacked_widget.setCurrentIndex(2)
                self.start_payment(self.pay_value)  # Переключаем диалог на режим ожидания
        else:
            self.reject(True)

    def accept_cash(self):
        self.payment_method = "cash_nobarcode"
        self.stacked_widget.setCurrentIndex(3)
        self.input_field_cash1.setFocus()

    # -------------------------------------------------------------

    def accept_cash_finnaly_list(self):
        try:
            input_value = self.input_field_cash1.text().replace(",", ".")
            if self.check_input_value(self.input_field_cash1, input_value):
                input_text = f"Получено: {input_value} ₽"
                out_value = float(input_value) - float(self.get_value())
                out_text = f"Сдача: {out_value} ₽"

                self.payment_label_cash_in.setText(input_text)
                self.payment_label_cash_out.setText(out_text)
                self.stacked_widget.setCurrentIndex(4)
                self.confirm_button_cash2.setFocus()
                self.input_field_cash1.setText("")
        except Exception as a:
            print(a)

    def back_cash(self):
        self.payment_method = None
        self.stacked_widget.setCurrentIndex(1)

    def back_card(self):
        self.payment_method = None
        if self.abort_file_created:
            self.abort_file_created = False
        if self.confirmed:
            self.confirmed = False
        self.stacked_widget.setCurrentIndex(1)

    # Payment methods -------------------------------------------------
    def start_payment(self, value):
        """Запуск процесса оплаты в отдельном потоке."""

        def rubles_to_kopecks(str_value):
            amount_in_rubles = float(str_value)  # Преобразуем строку в число (float)
            amount_in_kopecks = round(amount_in_rubles * 100)  # Преобразуем рубли в копейки
            return str(amount_in_kopecks)

        amount_in_kopecks = rubles_to_kopecks(value)
        args = ["1", amount_in_kopecks]  # Преобразуем сумму в копейки

        # Создание и запуск потока для процесса оплаты
        self.payment_thread = PaymentThread(args)
        self.payment_thread.payment_result_signal.connect(self.on_payment_result)
        self.payment_thread.start()

    def on_payment_result(self, exit_code):
        """Обработка результата оплаты."""
        if exit_code == 0:
            self.ok_valid()
        elif exit_code == 2000:
            self.back_card()
        else:
            self.other_code(exit_code)

    def ok_valid(self):
        QMessageBox.information(self, "Оплата", "Оплата выполнена успешно!", QMessageBox.Ok)
        self.accept()

    def other_code(self, exit_code):
        reply = QMessageBox.warning(self,
                                    "Ошибка оплаты",
                                    f"Не удалось провести оплату. Попробуйте снова?\nКод: {exit_code}",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.start_payment(self.pay_value)  # Повторить попытку оплаты
        elif reply == QMessageBox.No:
            self.reject(True)  # Отмена и выход

    def on_cancel(self):
        """Отмена оплаты: создаёт файл `POLLING.OFF` и блокирует кнопку"""
        if self.abort_file_created:
            return  # Если файл уже создан, ничего не делаем

        self.cancel_button_pay.setEnabled(False)  # Блокируем кнопку

        abort_file = r'C:\SC552\POLLING.OFF'
        try:
            with open(abort_file, "w") as f:
                f.write("ABORT")
            self.abort_file_created = True  # Устанавливаем флаг, что файл создан
            self.cancel_button_pay.setEnabled(True)  # Включаем кнопку обратно
        except Exception as e:
            print(f"Ошибка при создании файла отмены: {e}")
            self.cancel_button_pay.setEnabled(True)  # Включаем кнопку обратно
            return

    # -------------------------------------------------------------------

    def reject(self, exit_code=False):
        """Закрытие окна, если это допустимо"""
        if not exit_code:
            if self.stacked_widget.currentIndex() == 2:  # Если в режиме ожидания оплаты карты
                if not self.abort_file_created:
                    self.on_cancel()  # Создаем файл отмены
                    return  # Не закрываем окно сразу, ждем завершения процесса

        super().reject()  # Закрываем окно стандартным способом

    def check_input_value(self, input_label, input_value=False):
        valid_value = True
        value = input_label.text().replace(",", ".")

        if input_value:
            inspect_value = float(self.get_value()) > float(input_value)
            if inspect_value:
                QMessageBox.warning(self, "Ошибка", "Введенное значение меньше нужной суммы!", QMessageBox.Ok)
                valid_value = False
                input_label.setFocus()

        if not value:
            QMessageBox.warning(self, "Ошибка", "Поле не должно быть пустым", QMessageBox.Ok)
            valid_value = False
            input_label.setFocus()
        if not float(value) > 0:
            QMessageBox.warning(self, "Ошибка", "Значение должно быть больше нуля", QMessageBox.Ok)
            valid_value = False
            input_label.setFocus()

        return valid_value

    def get_value(self):
        return self.input_field.text().replace(",", ".")

    def keyPressEvent(self, event):
        """Обработка нажатия клавиши"""
        current_index = self.stacked_widget.currentIndex()
        if current_index == 0:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:  # Активация кнопки
                self.on_confirm()
        elif current_index == 1:
            if event.key() == Qt.Key_Right:  # Переключение вправо
                self.selected_index = 1  # Переключаем на "Карту"
                self.updateButtonStyles()  # Обновляем стили кнопок
            elif event.key() == Qt.Key_Left:  # Переключение влево
                self.selected_index = 0  # Переключаем на "Наличные"
                self.updateButtonStyles()  # Обновляем стили кнопок
            elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:  # Активация кнопки
                if self.selected_index == 0:
                    self.accept_cash()
                else:
                    self.accept_card()

        elif current_index == 2:
            if event.key() == Qt.Key_Escape:
                self.reject()
                return
        elif current_index == 3:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:  # Активация кнопки
                self.accept_cash_finnaly_list()

        elif current_index == 4:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:  # Активация кнопки
                self.ok_valid()

        if event.key() == Qt.Key_Escape:
            self.reject(True)
            return

    def get_payment_method(self):
        return self.payment_method

    def setButtonStyle(self, button, is_selected=False):
        """Изменяет стиль кнопки в зависимости от того, выбрана ли она"""
        background_color = "#01B4E4" if is_selected else "transparent"  # Определяем цвет фона
        button.setStyleSheet(f"""
                QPushButton {{
                    height: 80px;
                    font-size: 40px;
                    padding-right: 0px;
                    text-align: center;
                    border-radius: 10px;
                    border: 1px solid black;
                    background-color: {background_color};
                }}
            """)

    def updateButtonStyles(self):
        """Обновляет стиль кнопок в зависимости от выбранной"""
        self.setButtonStyle(self.cash_button, self.selected_index == 0)
        self.setButtonStyle(self.card_button, self.selected_index == 1)