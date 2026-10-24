from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QDoubleSpinBox, QSizePolicy, QMessageBox,
    QStackedWidget, QWidget, QSpacerItem
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt
from app.utils.payment_utils import PaymentThread, check_valid_terminal
from app.utils.get_path import get_resourse_path_icon


class FocusSpinBox(QDoubleSpinBox):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.focusPreviousChild()  # переходит к предыдущему виджету
        elif event.key() == Qt.Key_Down:
            self.focusNextChild()  # переходит к следующему виджету
        else:
            super().keyPressEvent(event)

class PaymentDialog(QDialog):
    def __init__(self, total_sum, number_order, parent=None):
        super().__init__()
        self.setFocus()
        self.setWindowTitle("Выбор метода оплаты")
        self.setFixedSize(1000, 600)

        self.total_sum = str(int(total_sum)) if total_sum == int(total_sum) else "{:.2f}".format(total_sum)
        self.number_order = number_order
        self.selected_method = None

        # Основной вертикальный layout
        self.layout = QVBoxLayout()
        self.initUI()
        self.setLayout(self.layout)
        self.stacked_widget.setCurrentIndex(0)

    def initUI(self):
        def create_check_layot():
            # Метка с суммой к оплате
            ckeck_layout = QHBoxLayout()

            self.check_label = QLabel(f"Оплата заказа")
            self.check_label.setStyleSheet("font-size:30px; color:#3F3F3F;padding-right:25px;")
            self.check_label.setAlignment(Qt.AlignCenter)

            self.check_label_value = QLabel(f"{self.number_order}")
            self.check_label_value.setStyleSheet(
                "font-size:32px; font-weight:700; color:white; background:#3F3F3F;")
            self.check_label_value.setAlignment(Qt.AlignCenter)

            self.check_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.check_label_value.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

            # Убираем растяжение между элементами
            ckeck_layout.setSpacing(0)

            # Выравнивание элементов по центру
            # ckeck_layout.setAlignment(Qt.AlignCenter)

            ckeck_layout.addStretch(1)
            ckeck_layout.addWidget(self.check_label)
            ckeck_layout.addWidget(self.check_label_value)
            ckeck_layout.addStretch(1)

            return ckeck_layout

        self.ckeck_layout = create_check_layot()
        self.layout.addLayout(self.ckeck_layout)
        # self.layout.addStretch(1)

        self.stacked_widget = QStackedWidget()

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
                self.setButtonStyle(self.cash_button,True)

                self.cash_button.clicked.connect(self.accept_cash)
                self.card_button.clicked.connect(self.accept_card)

                buttons_layout.addWidget(self.cash_button)
                buttons_layout.addWidget(self.card_button)

                return buttons_layout

            def create_amount_to_pay_layot():
                amount_layout = self.create_amount_to_pay_global()
                return amount_layout

            def create_combined_payment():
                self.combined_button = QPushButton("Комбинорованно")

                icon_combined_path = get_resourse_path_icon("combined.ico")
                self.combined_button.setIcon(QIcon(icon_combined_path))
                self.combined_button.setIconSize(QSize(55, 55))

                self.setButtonStyle(self.combined_button)

                self.combined_button.clicked.connect(self.combined_payment)
                return self.combined_button


            layout = QVBoxLayout()
            layout.addStretch(1)

            layout_amount_to_pay = create_amount_to_pay_layot()
            layout_buttonn_methods_pay = create_button_methods_pay()
            btn_combined = create_combined_payment()


            layout.addLayout(layout_amount_to_pay)
            layout.addStretch(1)
            layout.addLayout(layout_buttonn_methods_pay)
            layout.addWidget(btn_combined)
            return layout

        def create_layout_cash_page1():
            layout = QVBoxLayout()
            layout.addStretch(1)

            # Поле ввода суммы
            def create_amount_to_pay():
                amount_layout = QHBoxLayout()
                amount_layout.setAlignment(Qt.AlignCenter)  # Выравниваем весь layout по центру

                # Текст "К оплате:"
                amount_label = QLabel("К оплате:")
                amount_label.setStyleSheet("font-size:50px; color:#999999;")
                amount_label.setAlignment(Qt.AlignCenter)

                # Блок с суммой и валютой
                amount_layout_value = QHBoxLayout()
                amount_layout_value.setAlignment(Qt.AlignCenter)

                amount_label_value = QLabel(f"{self.total_sum}")
                amount_label_value.setStyleSheet("font-size:54px; color:#3D3D3D;margin-bottom:1px; "
                                                 "margin-left:10px;border-bottom: 3px solid #01B4E4;")
                amount_label_value.setAlignment(Qt.AlignCenter)

                amount_label_valute = QLabel("₽")
                amount_label_valute.setStyleSheet("font-size:56px; font-weight:500; color:#0A0A0A;padding-bottom:5px;")
                amount_label_valute.setAlignment(Qt.AlignCenter)

                # Добавляем сумму и знак валюты в общий блок
                amount_layout_value.addWidget(amount_label_value)
                amount_layout_value.addWidget(amount_label_valute)

                # Добавляем элементы в основной горизонтальный layout
                amount_layout.addStretch(1)  # Отступ слева для центрирования
                amount_layout.addWidget(amount_label)
                amount_layout.addSpacing(10)  # Маленький отступ между текстом и суммой
                amount_layout.addLayout(amount_layout_value)
                amount_layout.addStretch(1)  # Отступ справа для центрирования
                return amount_layout

            def create_received_input_layout():
                layout = QVBoxLayout()
                amount_input_text = QLabel("Получено:")
                amount_input_text.setStyleSheet("font-size:50px; color:#999999;")

                self.amount_input = QDoubleSpinBox(self)
                self.amount_input.setRange(0.0, 999999.99)  # Устанавливаем диапазон
                self.amount_input.setDecimals(2)  # Два знака после запятой
                self.amount_input.setSuffix(" ₽")  # Добавляем суффикс
                self.amount_input.setSingleStep(0.1)  # Шаг изменения

                self.amount_input.setStyleSheet("font-size:48px; height:65px;border-radius:10px;"
                                                "margin-bottom:60px;"
                                                "border:1px solid black;")
                # self.amount_input.setPlaceholderText("Введите сумму...")

                layout.addWidget(amount_input_text)
                layout.addWidget(self.amount_input)

                return layout

            def create_confirm_button():
                self.confirm_button_p1 = QPushButton("Продолжить")
                self.confirm_button_p1.setStyleSheet("font-size:45px; height:60px; background:#01B4E4; "
                                             "color:white; border-radius:10px;")
                self.confirm_button_p1.clicked.connect(self.calculate_change)
                return self.confirm_button_p1


            def create_widget_text_cash():
                label = QLabel("Оплата Наличными")
                label.setStyleSheet("font-size:44px; color:black; font-weight:700;")
                label.setAlignment(Qt.AlignCenter)
                return label

            # Кнопка подтверждения (скрыта)

            text_сash= create_widget_text_cash()

            # Кнопка подтверждения (скрыта)

            amount_to_pay = create_amount_to_pay()
            input_layout = create_received_input_layout()
            confirm_button = create_confirm_button()
            layout.addWidget(text_сash)
            layout.addStretch(1)
            layout.addLayout(amount_to_pay)
            layout.addStretch(1)
            layout.addLayout(input_layout)
            layout.addWidget(confirm_button)
            return layout

        def create_layout_cash_page2():
            layout = QVBoxLayout()
            layout.addStretch(1)

            def create_received_layout():
                amount_layout = QHBoxLayout()
                # amount_layout.setAlignment(Qt.AlignCenter)  # Выравниваем весь layout по центру

                # Текст "Получено:"
                amount_label = QLabel("Получено:")
                amount_label.setStyleSheet("font-size:48px; color:#999999;")
                # amount_label.setAlignment(Qt.AlignCenter)

                # Блок с суммой и валютой
                amount_layout_value = QHBoxLayout()
                # amount_layout_value.setAlignment(Qt.AlignCenter)


                self.received_label = QLabel("")
                self.received_label.setStyleSheet("font-size:50px; color:#3D3D3D;margin-bottom:1px; "
                                                 "margin-left:10px;border-bottom: 3px solid #01B4E4;")
                # amount_label_value.setAlignment(Qt.AlignCenter)

                amount_label_valute = QLabel("₽")
                amount_label_valute.setStyleSheet(
                    "font-size:52px; font-weight:500; color:#0A0A0A;padding-bottom:5px;")
                # amount_label_valute.setAlignment(Qt.AlignCenter)

                # Добавляем сумму и знак валюты в общий блок
                amount_layout_value.addWidget(self.received_label)
                amount_layout_value.addWidget(amount_label_valute)
                amount_layout_value.setContentsMargins(0, 0, 0, 0)
                amount_layout_value.setSpacing(0)

                # Добавляем элементы в основной горизонтальный layout
                # amount_layout.addStretch(1)  # Отступ слева для центрирования
                amount_layout.addWidget(amount_label)
                amount_layout.addStretch(1)
                amount_layout.addLayout(amount_layout_value)
                # amount_layout.addStretch(1)  # Отступ справа для центрирования
                return amount_layout

            def create_change_layout():
                amount_layout = QHBoxLayout()
                # amount_layout.setAlignment(Qt.AlignCenter)  # Выравниваем весь layout по центру

                # Текст "Получено:"
                amount_label = QLabel("Сдача:")
                amount_label.setStyleSheet("font-size:50px; color:#999999;")
                # amount_label.setAlignment(Qt.AlignCenter)

                # Блок с суммой и валютой
                amount_layout_value = QHBoxLayout()
                # amount_layout_value.setAlignment(Qt.AlignCenter)

                self.amount_change = QLabel("")
                self.amount_change.setStyleSheet("font-size:52px; color:#3D3D3D;margin-bottom:1px; "
                                                 f"border-bottom: 3px solid #01B4E4;font-weight:700;")
                # amount_label_value.setAlignment(Qt.AlignCenter)

                amount_label_valute = QLabel("₽")
                amount_label_valute.setStyleSheet("font-size:54px; font-weight:500; color:#0A0A0A;"
                                                  "padding-bottom:5px;padding-right:5px;")
                # amount_label_valute.setAlignment(Qt.AlignCenter)

                # Добавляем сумму и знак валюты в общий блок
                amount_layout_value.addWidget(self.amount_change)
                amount_layout_value.addWidget(amount_label_valute)
                amount_layout_value.setContentsMargins(0, 0, 0, 0)
                amount_layout_value.setSpacing(0)

                # Добавляем элементы в основной горизонтальный layout
                # amount_layout.addStretch(1)  # Отступ слева для центрирования
                amount_layout.addWidget(amount_label)
                amount_layout.addStretch(1)
                amount_layout.addLayout(amount_layout_value)
                # amount_layout.addStretch(1)  # Отступ справа для центрирования
                return amount_layout

            def create_to_pay_layout():
                amount_layout = QHBoxLayout()
                # amount_layout.setAlignment(Qt.AlignCenter)  # Выравниваем весь layout по центру

                # Текст "Получено:"
                amount_label = QLabel("К оплате:")
                amount_label.setStyleSheet("font-size:48px; color:#999999;")
                # amount_label.setAlignment(Qt.AlignCenter)

                # Блок с суммой и валютой
                amount_layout_value = QHBoxLayout()
                # amount_layout_value.setAlignment(Qt.AlignCenter)

                amount_label_value = QLabel(f"{self.total_sum}")
                amount_label_value.setStyleSheet("font-size:50px; color:#3D3D3D;margin-bottom:1px;  "
                                                 "margin-left:10px;border-bottom: 3px solid #01B4E4;")
                # amount_label_value.setAlignment(Qt.AlignCenter)

                amount_label_valute = QLabel("₽")
                amount_label_valute.setStyleSheet(
                    "font-size:52px; font-weight:500; color:#0A0A0A;padding-bottom:5px;")
                # amount_label_valute.setAlignment(Qt.AlignCenter)

                # Добавляем сумму и знак валюты в общий блок
                amount_layout_value.addWidget(amount_label_value)
                amount_layout_value.addWidget(amount_label_valute)
                amount_layout_value.setContentsMargins(0, 0, 0, 0)
                amount_layout_value.setSpacing(0)


                # Добавляем элементы в основной горизонтальный layout
                # amount_layout.addStretch(1)  # Отступ слева для центрирования
                amount_layout.addWidget(amount_label)
                amount_layout.addStretch(1)
                amount_layout.addLayout(amount_layout_value)
                # amount_layout.addStretch(1)  # Отступ справа для центрирования
                return amount_layout

            def create_close_pay_button():
                # Кнопка завершения покупки (скрыта)
                complete_button = QPushButton("Завершить покупку")
                complete_button.setStyleSheet("height:60px; font-size:45px; background:#4CAF50; color:white;border-radius:15px;")
                complete_button.clicked.connect(self.complete_purchase)
                return complete_button

            def create_widget_text_cash():
                label = QLabel("Оплата Наличными")
                label.setStyleSheet("font-size:44px; color:black; font-weight:700;")
                label.setAlignment(Qt.AlignCenter)
                return label

                # Кнопка подтверждения (скрыта)

            text_сash = create_widget_text_cash()

            received_layout = create_received_layout()
            change_layout = create_change_layout()
            to_pay_layout = create_to_pay_layout()
            close_pay_button = create_close_pay_button()

            one_line_general_money_layout = QHBoxLayout()
            two_line_general_money_layout = QHBoxLayout()

            one_line_general_money_layout.addLayout(to_pay_layout)
            one_line_general_money_layout.addLayout(received_layout)
            two_line_general_money_layout.addLayout(change_layout)
            two_line_general_money_layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding))  # Вторая половина пустая

            layout.addWidget(text_сash)
            layout.addStretch(1)
            layout.addLayout(one_line_general_money_layout)
            layout.addStretch(1)
            layout.addLayout(two_line_general_money_layout)
            layout.addStretch(1)
            layout.addWidget(close_pay_button)
            return layout

        def create_layout_card_page():
            layout = QVBoxLayout()

            def create_text_wait_layout():
                layout = QHBoxLayout()
                text_wait = QLabel("Касса ждёт оплаты ... ")
                text_wait.setStyleSheet("font-size:55px; padding-top:70px;")
                layout.addStretch(1)
                layout.addWidget(text_wait)
                layout.addStretch(1)
                return layout

            def create_text_value_layout():
                amount_layout = QHBoxLayout()
                amount_layout.setAlignment(Qt.AlignCenter)  # Выравниваем весь layout по центру

                # Текст "К оплате:"
                amount_label = QLabel("К оплате:")
                amount_label.setStyleSheet("font-size:45px; color:#999999;")
                amount_label.setAlignment(Qt.AlignCenter)

                # Блок с суммой и валютой
                amount_layout_value = QHBoxLayout()
                amount_layout_value.setAlignment(Qt.AlignCenter)

                self.amount_label_value_card = QLabel(f"{self.total_sum}")
                self.amount_label_value_card.setStyleSheet("font-size:50px; color:#3D3D3D;margin-bottom:1px; "
                                                 "margin-left:10px;border-bottom: 3px solid #01B4E4;")
                self.amount_label_value_card.setAlignment(Qt.AlignCenter)

                amount_label_valute = QLabel("₽")
                amount_label_valute.setStyleSheet("font-size:52px; font-weight:500; color:#0A0A0A;padding-bottom:5px;")
                amount_label_valute.setAlignment(Qt.AlignCenter)

                # Добавляем сумму и знак валюты в общий блок
                amount_layout_value.addWidget(self.amount_label_value_card)
                amount_layout_value.addWidget(amount_label_valute)

                # Добавляем элементы в основной горизонтальный layout
                amount_layout.addStretch(1)  # Отступ слева для центрирования
                amount_layout.addWidget(amount_label)
                amount_layout.addSpacing(10)  # Маленький отступ между текстом и суммой
                amount_layout.addLayout(amount_layout_value)
                amount_layout.addStretch(1)  # Отступ справа для центрирования
                return amount_layout

            def create_button_cancel_pay_layout():
                # Создаем и показываем кнопку "Отмена"
                self.cancel_button_card = QPushButton("Отмена")
                self.cancel_button_card.setStyleSheet("font-size:45px; height:60px; border-radius: 15px; border:1px solid black; background-color:#FFD701;")
                self.cancel_button_card.clicked.connect(self.create_file_for_cancel_card_pay)

                self.abort_file_created = False  # Флаг: был ли уже создан файл

                return self.cancel_button_card

            text_wait_layout = create_text_wait_layout()
            text_value_layout = create_text_value_layout()
            button_cancel_pay_layout = create_button_cancel_pay_layout()

            layout.addLayout(text_wait_layout)
            layout.addStretch(1)
            layout.addLayout(text_value_layout)
            layout.addStretch(1)
            layout.addWidget(button_cancel_pay_layout)
            return layout

        def create_layout_combined_page1():
            layout = QVBoxLayout()
            layout.addStretch(1)

            # Поле ввода суммы
            def create_amount_to_pay():
                amount_layout = QHBoxLayout()
                amount_layout.setAlignment(Qt.AlignCenter)  # Выравниваем весь layout по центру

                # Текст "К оплате:"
                amount_label = QLabel("К оплате:")
                amount_label.setStyleSheet("font-size:50px; color:#999999;")
                amount_label.setAlignment(Qt.AlignCenter)

                # Блок с суммой и валютой
                amount_layout_value = QHBoxLayout()
                amount_layout_value.setAlignment(Qt.AlignCenter)

                amount_label_value = QLabel(f"{self.total_sum}")
                amount_label_value.setStyleSheet("font-size:54px; color:#3D3D3D;margin-bottom:1px; "
                                                 "margin-left:10px;border-bottom: 3px solid #01B4E4;")
                amount_label_value.setAlignment(Qt.AlignCenter)

                amount_label_valute = QLabel("₽")
                amount_label_valute.setStyleSheet("font-size:56px; font-weight:500; color:#0A0A0A;padding-bottom:5px;")
                amount_label_valute.setAlignment(Qt.AlignCenter)

                # Добавляем сумму и знак валюты в общий блок
                amount_layout_value.addWidget(amount_label_value)
                amount_layout_value.addWidget(amount_label_valute)

                # Добавляем элементы в основной горизонтальный layout
                amount_layout.addStretch(1)  # Отступ слева для центрирования
                amount_layout.addWidget(amount_label)
                amount_layout.addSpacing(10)  # Маленький отступ между текстом и суммой
                amount_layout.addLayout(amount_layout_value)
                amount_layout.addStretch(1)  # Отступ справа для центрирования
                return amount_layout

            def create_received_cash_input_layout():
                layout = QVBoxLayout()
                amount_input_text = QLabel("Получено наличными:")
                amount_input_text.setStyleSheet("font-size:40px; color:#999999;")

                self.amount_input_cash = FocusSpinBox(self)
                self.amount_input_cash.setRange(0.0, 999999.99)  # Устанавливаем диапазон
                self.amount_input_cash.setDecimals(2)  # Два знака после запятой
                self.amount_input_cash.setSuffix(" ₽")  # Добавляем суффикс
                self.amount_input_cash.setSingleStep(0.1)  # Шаг изменения

                self.amount_input_cash.setStyleSheet("font-size:38px; height:45px;border-radius:5px;"
                                                "margin-bottom:20px;"
                                                "border:1px solid black;")
                # self.amount_input.setPlaceholderText("Введите сумму...")

                layout.addWidget(amount_input_text)
                layout.addWidget(self.amount_input_cash)

                return layout

            def create_received_card_input_layout():
                layout = QVBoxLayout()
                amount_input_text = QLabel("Получено картой:")
                amount_input_text.setStyleSheet("font-size:40px; color:#999999;")

                self.amount_input_card = FocusSpinBox(self)
                self.amount_input_card.setRange(0.0, 999999.99)  # Устанавливаем диапазон
                self.amount_input_card.setDecimals(2)  # Два знака после запятой
                self.amount_input_card.setSuffix(" ₽")  # Добавляем суффикс
                self.amount_input_card.setSingleStep(0.1)  # Шаг изменения

                self.amount_input_card.setStyleSheet("font-size:38px; height:45px;border-radius:5px;"
                                                "margin-bottom:20px;"
                                                "border:1px solid black;")
                # self.amount_input.setPlaceholderText("Введите сумму...")

                layout.addWidget(amount_input_text)
                layout.addWidget(self.amount_input_card)

                return layout

            def create_confirm_button():
                self.confirm_button_combined_1 = QPushButton("Продолжить")
                self.confirm_button_combined_1.setStyleSheet("font-size:45px; height:60px; background:#01B4E4; "
                                                     "color:white; border-radius:10px;")
                self.confirm_button_combined_1.clicked.connect(self.combine_page2)
                return self.confirm_button_combined_1

            def create_widget_text_combined():
                label = QLabel("Комбинированная оплата")
                label.setStyleSheet("font-size:44px; color:black; font-weight:700;")
                label.setAlignment(Qt.AlignCenter)
                return label

            # Кнопка подтверждения (скрыта)

            text_combined = create_widget_text_combined()
            amount_to_pay = create_amount_to_pay()
            input_layout_cash = create_received_cash_input_layout()
            input_layout_card = create_received_card_input_layout()
            confirm_button = create_confirm_button()

            layout.addWidget(text_combined)
            layout.addStretch(1)
            layout.addLayout(amount_to_pay)
            layout.addStretch(1)
            layout.addLayout(input_layout_cash)
            layout.addLayout(input_layout_card)
            layout.addWidget(confirm_button)

            self.amount_input_cash.valueChanged.connect(self.on_cash_combined_changed)
            self.amount_input_card.valueChanged.connect(self.on_card_combined_changed)

            self.amount_input_card.setFocusPolicy(Qt.StrongFocus)
            self.amount_input_cash.setFocusPolicy(Qt.StrongFocus)
            return layout

        def create_layout_combined_page2():
            layout = QVBoxLayout()
            layout.addStretch(1)

            # Поле ввода суммы
            def create_amount_to_pay():
                amount_layout = QHBoxLayout()
                amount_layout.setAlignment(Qt.AlignCenter)  # Выравниваем весь layout по центру

                # Текст "К оплате:"
                amount_label = QLabel("К оплате наличными:")
                amount_label.setStyleSheet("font-size:50px; color:#999999;")
                amount_label.setAlignment(Qt.AlignCenter)

                # Блок с суммой и валютой
                amount_layout_value = QHBoxLayout()
                amount_layout_value.setAlignment(Qt.AlignCenter)

                value = self.trim_trailing_zeros(self.amount_input_cash.value())


                self.amount_label_value_combined_2 = QLabel(value)
                self.amount_label_value_combined_2.setStyleSheet("font-size:54px; color:#3D3D3D;margin-bottom:1px; "
                                                 "margin-left:10px;border-bottom: 3px solid #01B4E4;")
                self.amount_label_value_combined_2.setAlignment(Qt.AlignCenter)

                amount_label_valute = QLabel("₽")
                amount_label_valute.setStyleSheet("font-size:56px; font-weight:500; color:#0A0A0A;padding-bottom:5px;")
                amount_label_valute.setAlignment(Qt.AlignCenter)

                # Добавляем сумму и знак валюты в общий блок
                amount_layout_value.addWidget(self.amount_label_value_combined_2)
                amount_layout_value.addWidget(amount_label_valute)

                # Добавляем элементы в основной горизонтальный layout
                amount_layout.addStretch(1)  # Отступ слева для центрирования
                amount_layout.addWidget(amount_label)
                amount_layout.addSpacing(10)  # Маленький отступ между текстом и суммой
                amount_layout.addLayout(amount_layout_value)
                amount_layout.addStretch(1)  # Отступ справа для центрирования
                return amount_layout

            def create_received_cash_input_layout():
                layout = QVBoxLayout()
                amount_input_text = QLabel("Получено наличными:")
                amount_input_text.setStyleSheet("font-size:34px; color:#999999;")

                self.amount_input_cash_2 = QDoubleSpinBox(self)
                self.amount_input_cash_2.setRange(0.0, 999999.99)  # Устанавливаем диапазон
                self.amount_input_cash_2.setDecimals(2)  # Два знака после запятой
                self.amount_input_cash_2.setSuffix(" ₽")  # Добавляем суффикс
                self.amount_input_cash_2.setSingleStep(0.1)  # Шаг изменения
                self.amount_input_cash_2.setMinimum(float(self.amount_input_cash.value()))
                self.amount_input_cash_2.setValue(float(self.amount_input_cash.value()))

                self.amount_input_cash_2.setStyleSheet("font-size:38px; height:45px;border-radius:5px;"
                                                "margin-bottom:20px;"
                                                "border:1px solid black;")
                # self.amount_input.setPlaceholderText("Введите сумму...")

                layout.addWidget(amount_input_text)
                layout.addWidget(self.amount_input_cash_2)

                return layout

            def create_money_change_layout():
                amount_layout = QHBoxLayout()
                amount_layout.setAlignment(Qt.AlignLeft)  # Выравниваем весь layout по центру

                amount_label = QLabel("Cдача:")
                amount_label.setStyleSheet("font-size:40px; color:#999999;")

                # Блок с суммой и валютой
                amount_layout_value = QHBoxLayout()
                amount_layout_value.setAlignment(Qt.AlignCenter)

                value = self.trim_trailing_zeros(self.amount_input_cash_2.value() - self.amount_input_cash.value())

                self.amount_label_value_combined = QLabel(f"{value}")
                self.amount_label_value_combined.setStyleSheet("font-size:54px; color:#3D3D3D;margin-bottom:1px; "
                                                 "margin-left:10px;border-bottom: 3px solid #01B4E4; font-weight:700;")
                self.amount_label_value_combined.setAlignment(Qt.AlignCenter)

                amount_label_valute = QLabel("₽")
                amount_label_valute.setStyleSheet("font-size:56px; font-weight:500; color:#0A0A0A;padding-bottom:5px;")
                amount_label_valute.setAlignment(Qt.AlignCenter)

                # Добавляем сумму и знак валюты в общий блок
                amount_layout_value.addWidget(self.amount_label_value_combined)
                amount_layout_value.addWidget(amount_label_valute)

                # Добавляем элементы в основной горизонтальный layout
                # amount_layout.addStretch(1)  # Отступ слева для центрирования
                amount_layout.addWidget(amount_label)
                amount_layout.addSpacing(10)  # Маленький отступ между текстом и суммой
                amount_layout.addLayout(amount_layout_value)
                # amount_layout.addStretch(1)  # Отступ справа для центрирования

                return amount_layout

            def create_confirm_button():
                self.confirm_button_combined_2 = QPushButton("Продолжить")
                self.confirm_button_combined_2.setStyleSheet("font-size:45px; height:60px; background:#01B4E4; "
                                                     "color:white; border-radius:10px;")
                self.confirm_button_combined_2.clicked.connect(self.combine_page3)
                return self.confirm_button_combined_2


            def create_widget_text_combined():
                label = QLabel("Комбинированная оплата")
                label.setStyleSheet("font-size:44px; color:black; font-weight:700;")
                label.setAlignment(Qt.AlignCenter)
                return label

            # Кнопка подтверждения (скрыта)

            text_combined = create_widget_text_combined()


            # Кнопка подтверждения (скрыта)
            amount_to_pay = create_amount_to_pay()
            input_layout_cash = create_received_cash_input_layout()
            money_change_layout = create_money_change_layout()
            confirm_button = create_confirm_button()

            layout.addWidget(text_combined)
            layout.addStretch(1)
            layout.addLayout(amount_to_pay)
            layout.addStretch(1)
            layout.addLayout(input_layout_cash)
            layout.addLayout(money_change_layout)
            layout.addWidget(confirm_button)

            self.amount_input_cash_2.valueChanged.connect(self.on_cash2_combined_changed)
            return layout





        self.choose_methods_pay_page = QWidget()
        self.layout_choose_methods_pay = create_layout_choose_methods_pay()
        self.choose_methods_pay_page.setLayout(self.layout_choose_methods_pay)
        self.stacked_widget.addWidget(self.choose_methods_pay_page)

        self.cash_page1 = QWidget()
        self.layout_page1 = create_layout_cash_page1()
        self.cash_page1.setLayout(self.layout_page1)
        self.stacked_widget.addWidget(self.cash_page1)

        self.cash_page2 = QWidget()
        self.layout_page2 = create_layout_cash_page2()
        self.cash_page2.setLayout(self.layout_page2)
        self.stacked_widget.addWidget(self.cash_page2)

        self.card_page = QWidget()
        self.card_layout_page = create_layout_card_page()
        self.card_page.setLayout(self.card_layout_page)
        self.stacked_widget.addWidget(self.card_page)

        self.combined_page1 = QWidget()
        self.layout_combined_page1 = create_layout_combined_page1()
        self.combined_page1.setLayout(self.layout_combined_page1)
        self.stacked_widget.addWidget(self.combined_page1)

        self.combined_page2 = QWidget()
        self.layout_combined_page2 = create_layout_combined_page2()
        self.combined_page2.setLayout(self.layout_combined_page2)
        self.stacked_widget.addWidget(self.combined_page2)

        self.layout.addWidget(self.stacked_widget)


    # Сash Management
    def accept_cash(self):
        """При выборе наличных скрывает кнопки выбора и показывает ввод суммы."""
        self.selected_method = "cash"
        self.stacked_widget.setCurrentIndex(1)
        # Убираем начальное значение
        self.amount_input.setSpecialValueText("")  # Делает поле пустым при запуске
        self.amount_input.clear()  # Очищаем текущее значение
        self.amount_input.setFocus()

    def calculate_change(self):
        """Рассчитывает сдачу после ввода суммы и отображает результаты."""
        given_amount = self.amount_input.value()
        if given_amount < float(self.total_sum):
            QMessageBox.warning(self, "Ошибка", "Недостаточно средств!")
            self.amount_input.setSpecialValueText("")  # Делает поле пустым при запуске
            self.amount_input.clear()  # Очищаем текущее значение
            self.amount_input.setFocus()
            return
        else:
            try:
                received_text = self.trim_trailing_zeros(self.amount_input.value())
                change_text = self.trim_trailing_zeros(self.amount_input.value() - float(self.total_sum))
                self.received_label.setText(received_text)
                self.amount_change.setText(change_text)
                self.stacked_widget.setCurrentIndex(2)
            except Exception as a:
                print(a)

    def trim_trailing_zeros(self, value):
        """Удаляет только лишние нули после запятой и точку, если она не нужна"""
        if isinstance(value, (float, int)):
            value = f"{value:.10f}"  # округлим до 10 знаков, чтобы убрать мусор float
        if '.' in value:
            value = value.rstrip('0').rstrip('.')
        return value

    # Transaction Management
    def accept_card(self):
        """При выборе карты скрывает кнопки выбора и показывает кнопку 'Отмена'."""
        if check_valid_terminal(self):
            self.selected_method = "card"
            self.stacked_widget.setCurrentIndex(3)

            value = self.trim_trailing_zeros(self.total_sum)
            str_value = str(value)

            self.amount_label_value_card.setText(value)

            try:
                self.start_payment(self.total_sum)
            except Exception as a:
                print(a)
        else:
            self.stacked_widget.setCurrentIndex(0)

    def start_payment(self, value):
        """Запуск процесса оплаты в отдельном потоке."""
        def rubles_to_kopecks(str_value):
            amount_in_rubles = float(str_value) # Преобразуем строку в число (float)
            amount_in_kopecks = round(amount_in_rubles * 100) # Преобразуем рубли в копейки
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
            self.complete_purchase()
        elif exit_code == 2000:
            self.cancel_payment()
        else:
            self.cancel_other_exit_code_pay(exit_code)

    def cancel_other_exit_code_pay(self, exit_code):
        reply = QMessageBox.warning(self,
                                    "Ошибка оплаты",
                                    f"Не удалось провести оплату. Попробуйте снова?\nКод: {exit_code}",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.start_payment(self.total_sum)  # Повторить попытку оплаты
        elif reply == QMessageBox.No:
            self.reject(False)  # Отмена и выход

    # -------------------------------------------------------------------------------------
    def combined_payment(self):
        try:
            self.selected_method = "combined"
            self.stacked_widget.setCurrentIndex(4)
            # Убираем начальное значение
            self.amount_input_card.setSpecialValueText("")  # Делает поле пустым при запуске
            self.amount_input_card.clear()  # Очищаем текущее значение
            self.amount_input_cash.setFocus()
            self.amount_input_cash.setSpecialValueText("")  # Делает поле пустым при запуске
            self.amount_input_cash.clear()  # Очищаем текущее значение
        except Exception as a:
            print(a)

    def combine_page2(self):
        if self.amount_input_card.value() == 0.00 or self.amount_input_cash.value() == 0.00:
            QMessageBox.warning(self, "Ошибка", "Оба значения должны быть больше 0!")
        elif self.amount_input_card.value() + self.amount_input_cash.value() != float(self.total_sum):
            QMessageBox.warning(self, "Ошибка", "Сумма должна быть равна общему значению!")
        else:
            self.amount_input_cash_2.setFocus()
            self.amount_input_cash_2.setSpecialValueText("")  # Делает поле пустым при запуске
            self.amount_input_cash_2.setValue(float(self.amount_input_cash.value()))
            self.amount_input_cash_2.lineEdit().selectAll()

            value = self.trim_trailing_zeros(float(self.amount_input_cash.value()))
            self.amount_label_value_combined_2.setText(value)

            self.stacked_widget.setCurrentIndex(5)

    def combine_page3(self):
        if self.amount_input_cash_2.value() < self.amount_input_cash.value():
            value_message = self.trim_trailing_zeros(self.amount_input_cash.value())
            QMessageBox.warning(self, "Ошибка", f"Значение должно быть не менее {value_message} руб.")
            self.amount_input_cash_2.setValue(self.amount_input_cash.value())
            self.amount_input_cash_2.setFocus()

        else:
            if check_valid_terminal(self):
                value = self.trim_trailing_zeros(self.amount_input_card.value())
                str_value = str(value)
                self.amount_label_value_card.setText(value)

                self.stacked_widget.setCurrentIndex(3)

                try:
                    self.start_payment(str_value)
                except Exception as a:
                    print(a)
            else:
                self.stacked_widget.setCurrentIndex(0)

    def on_cash_combined_changed(self, value):
        max_value = float(self.total_sum)
        if value > max_value:
            value = max_value
            self.amount_input_cash.blockSignals(True)
            self.amount_input_cash.setValue(value)
            self.amount_input_cash.blockSignals(False)

        remaining = round(float(self.total_sum) - value, 2)
        if remaining < 0.0:
            remaining = 0.0

        self.amount_input_card.blockSignals(True)
        if self.amount_input_card.value() != remaining:
            self.amount_input_card.setValue(remaining)
        self.amount_input_card.blockSignals(False)

    def on_card_combined_changed(self, value):
        max_value = float(self.total_sum)
        if value > max_value:
            value = max_value
            self.amount_input_card.blockSignals(True)
            self.amount_input_card.setValue(value)
            self.amount_input_card.blockSignals(False)

        remaining = round(float(self.total_sum) - value, 2)
        if remaining < 0.0:
            remaining = 0.0

        self.amount_input_cash.blockSignals(True)
        if self.amount_input_cash.value() != remaining:
            self.amount_input_cash.setValue(remaining)
        self.amount_input_cash.blockSignals(False)

    def on_cash2_combined_changed(self, value):
        if value < self.amount_input_cash.value():
            value = float(self.amount_input_cash.value())
            self.amount_input_cash_2.setValue(value)
            self.amount_input_cash_2.lineEdit().selectAll()
        value_ = self.trim_trailing_zeros(self.amount_input_cash_2.value() - self.amount_input_cash.value())
        self.amount_label_value_combined.setText(value_)

    def get_cash_combine(self):
        return self.amount_input_cash.value()

    def get_card_combine(self):
        return self.amount_input_card.value()


    # Utility functions

    def cancel_payment(self):
        """Отмена оплаты и возврат к выбору метода оплаты."""
        self.stacked_widget.setCurrentIndex(0)
        self.setFocus()
        self.abort_file_created = False
        self.cancel_button_card.setEnabled(True)

    def complete_purchase(self):
        """Завершаем покупку и закрываем диалог."""
        QMessageBox.information(self, "Покупка", "Покупка завершена!")
        self.accept()

    def get_selected_method(self):
        return self.selected_method

    def reject(self, is_valid_terminal=True):
        if is_valid_terminal:
            # Это будет вызвано при нажатии на "Отмена" или при закрытии окна
            if self.stacked_widget.currentIndex() == 3:
                # Если файл не был создан, не закрываем окно
                if not self.abort_file_created:
                    return  # Возвращаемся, не закрывая окно
                self.create_file_for_cancel_card_pay()

        # Если файл создан, закрываем окно
        super().reject()  # Это необходимо для стандартного поведения (закрытие окна)

    def create_file_for_cancel_card_pay(self):
        """Отмена оплаты (создаёт файл `POLLING.OFF`)"""
        if self.abort_file_created:
            return  # Если файл уже создан, ничего не делаем

        self.cancel_button_card.setEnabled(False)  # Отключаем кнопку

        abort_file = r'C:\SC552\POLLING.OFF'
        try:
            with open(abort_file, "w") as f:
                f.write("ABORT")
            self.abort_file_created = True  # Устанавливаем флаг, что файл создан
        except Exception as e:
            self.cancel_button_card.setEnabled(True)  # Включаем кнопку обратно в случае ошибки
            return


    def keyPressEvent(self, event):
        """Обрабатываем нажатие клавиш"""
        current_index = self.stacked_widget.currentIndex()

        if current_index == 0:
            index = self.selected_index
            if event.key() == Qt.Key_Escape:
                self.reject()
            elif event.key() == Qt.Key_Right:  # Переключение вправо
                if self.selected_index == 2:
                    self.selected_index = 0
                else:
                    self.selected_index += 1  # Переключаем на "Карту"
                self.updateButtonStyles()  # Обновляем стили кнопок
            elif event.key() == Qt.Key_Left:  # Переключение влево
                if self.selected_index == 0:
                    self.selected_index = 2
                else:
                    self.selected_index -= 1  # Переключаем на "Наличные"
                self.updateButtonStyles()  # Обновляем стили кнопок
            elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:  # Активация кнопки
                dct_methods = {0:self.accept_cash, 1: self.accept_card, 2: self.combined_payment}
                activate_method = dct_methods.get(self.selected_index, 0)
                activate_method()


        elif current_index == 1:
            if event.key() == Qt.Key_Escape:
                self.cancel_payment()
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.calculate_change()

        elif current_index == 2:
            if event.key() == Qt.Key_Escape:
                self.cancel_payment()
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.complete_purchase()

        elif current_index == 3:
            if event.key() == Qt.Key_Escape:
                self.create_file_for_cancel_card_pay()
            if event.key() == Qt.Key_Backspace:
                self.create_file_for_cancel_card_pay()

        elif current_index == 4:
            if event.key() == Qt.Key_Escape:
                self.stacked_widget.setCurrentIndex(0)
            elif event.key() == Qt.Key_Backspace:
                self.stacked_widget.setCurrentIndex(0)

            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.combine_page2()
        elif current_index == 5:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.combine_page3()
            elif event.key() == Qt.Key_Escape:
                self.combined_payment()
            elif event.key() == Qt.Key_Backspace:
                self.combined_payment()





    # Helper Functions

    def format_number(self, value):
            return str(value).rstrip("0").rstrip(".")

    def create_amount_to_pay_global(self):
        amount_layout = QHBoxLayout()
        amount_layout.setAlignment(Qt.AlignCenter)  # Выравниваем весь layout по центру

        # Текст "К оплате:"
        amount_label = QLabel("К оплате:")
        amount_label.setStyleSheet("font-size:50px; color:#999999;")
        amount_label.setAlignment(Qt.AlignCenter)

        # Блок с суммой и валютой
        amount_layout_value = QHBoxLayout()
        amount_layout_value.setAlignment(Qt.AlignCenter)

        amount_label_value = QLabel(f"{self.total_sum}")
        amount_label_value.setStyleSheet("font-size:52px; color:#3D3D3D;margin-bottom:1px; "
                                         "margin-left:10px;border-bottom: 3px solid #01B4E4;")
        amount_label_value.setAlignment(Qt.AlignCenter)

        amount_label_valute = QLabel("₽")
        amount_label_valute.setStyleSheet("font-size:54px; font-weight:500; color:#0A0A0A;padding-bottom:5px;")
        amount_label_valute.setAlignment(Qt.AlignCenter)

        # Добавляем сумму и знак валюты в общий блок
        amount_layout_value.addWidget(amount_label_value)
        amount_layout_value.addWidget(amount_label_valute)

        # Добавляем элементы в основной горизонтальный layout
        amount_layout.addStretch(1)  # Отступ слева для центрирования
        amount_layout.addWidget(amount_label)
        amount_layout.addSpacing(10)  # Маленький отступ между текстом и суммой
        amount_layout.addLayout(amount_layout_value)
        amount_layout.addStretch(1)  # Отступ справа для центрирования
        return amount_layout

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
        self.setButtonStyle(self.combined_button, self.selected_index == 2)