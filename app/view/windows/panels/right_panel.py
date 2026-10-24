from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QGridLayout,
    QSizePolicy,
)
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

from utils.get_path import get_resourse_path_icon
from search_global import create_search_result_list


class RightPanel(QWidget):
    def __init__(self, presenter, parent=None):
        super().__init__(parent)

        self.presenter = presenter
        self.main_window = parent

        self.init_ui()

    def init_ui(self):
        font_size_digit_btn = 44

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Сетка цифровой клавиатуры
        digit_widget = QWidget(self)
        digit_layout = QGridLayout(digit_widget)
        digit_layout.setSpacing(5)
        digit_layout.setContentsMargins(0, 0, 0, 0)

        digit_widget.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        # --------------------------------------------------
        # Вспомогательные функции настройки кнопок
        # --------------------------------------------------

        def set_settings_button_mini(
            button,
            func,
            bkgrnd_clr,
            color,
            position,
            path=None,
            font_size=20,
            size=(50, 50),
        ):
            if path:
                icon = QIcon(path)
                button.setIcon(icon)
                button.setIconSize(QSize(*size))

            button.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Expanding,
            )
            button.setStyleSheet(
                f"font-size: {font_size}px;"
                f"background-color: {bkgrnd_clr};"
                f"color: {color};"
                f"border-radius: 10px;"
                f"padding: 10px;"
                f"border: 2px solid black;"
            )

            button.clicked.connect(func)
            digit_layout.addWidget(button, *position)

        def set_settings_button_big(button:QPushButton,func=None,is_enable=True,height=75):
            button.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
            button.setStyleSheet("border-radius: 10px; border: 2px solid black; font-size: 20px;")
            button.setFixedHeight(height)
            button.setEnabled(is_enable)

            layout.addWidget(button)
            button.clicked.connect(lambda checked=False: func())

        # --------------------------------------------------
        # Поле ввода штрихкода
        # --------------------------------------------------

        self.barcode_edit = QLineEdit(self)
        self.barcode_edit.setMaxLength(13)

        self.barcode_edit.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.barcode_edit.setStyleSheet(
            "border-radius: 10px;"
            "border: 1px solid #78788D;"
            "font-size: 26px;"
            "padding: 20px;"
            "margin-bottom: 20px;"
            "margin-top: 10px;"
            "padding-left: 5px;"
        )
        self.barcode_edit.setPlaceholderText("Введите штрих-код...")
        self.barcode_edit.setFixedHeight(90)

        layout.addWidget(self.barcode_edit)

        self.barcode_edit.returnPressed.connect(self.presenter.process_barcode)
        self.barcode_edit.textChanged.connect(self.presenter.get_list_product_on_keypress)

        # Список результатов поиска.
        # Пока сохраняем прежний родительский объект и поведение.
        self.list_search_product = create_search_result_list(self.main_window,self.main_window.left_panel.product_name_label)

        self.list_search_product.itemClicked.connect(self.presenter.select_item_for_search)

        # --------------------------------------------------
        # Цифровая клавиатура
        # --------------------------------------------------

        def add_digit(digit):
            current_text = self.barcode_edit.text()
            self.barcode_edit.setText(current_text + str(digit))

        for i in range(10):
            digit = i + 1
            row = i // 3
            col = i % 3

            if i == 9:
                row = 3
                col = 1
                digit = 0

            button = QPushButton(str(digit), digit_widget)
            button.clicked.connect(lambda _, d=digit: add_digit(d))
            button.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
            button.setStyleSheet(
                f"font-size: {font_size_digit_btn}px;"
                "background-color: #F3F3F3;"
                "color: black;"
                "border-radius: 10px;"
                "border: 2px solid black;"
                "padding: 10px;"
            )

            digit_layout.addWidget(button, row, col)

        # --------------------------------------------------
        # Действия с полем штрихкода
        # --------------------------------------------------

        def delete_last_character():
            current_text = self.barcode_edit.text()

            if current_text:
                self.barcode_edit.setText(current_text[:-1])

        def clear_input_field():
            self.barcode_edit.clear()

        icon_path_delete = get_resourse_path_icon("delete.ico")
        icon_path_confirm = get_resourse_path_icon("enter.ico")
        icon_path_clear = get_resourse_path_icon("clear.ico")

        self.delete_last_char_button = QPushButton("", self)
        set_settings_button_mini(self.delete_last_char_button,delete_last_character,"#FFD701","white",(3, 0),path=icon_path_delete,size=(50, 50))

        self.confirm_button = QPushButton("", self)
        set_settings_button_mini(self.confirm_button,self.presenter.process_barcode,"#82D368","white",(3, 2),path=icon_path_confirm,size=(50, 50))

        self.increment_button = QPushButton("+", self)
        set_settings_button_mini(self.increment_button,self.increment_quantity,"#F3F3F3","black",(4, 1),font_size=font_size_digit_btn)

        self.decrement_button = QPushButton("-", self)
        set_settings_button_mini(self.decrement_button,self.decrement_quantity,"#F3F3F3","black",(4, 2),font_size=font_size_digit_btn)

        self.clear_button = QPushButton("", self)
        set_settings_button_mini(self.clear_button,clear_input_field,"#F75C5E","white",(4, 0), path=icon_path_clear,size=(40, 40))

        digit_widget.setLayout(digit_layout)
        layout.addWidget(digit_widget)

        # --------------------------------------------------
        # Основные кнопки действий
        # --------------------------------------------------

        self.edit_quantity_button = QPushButton("Изменить кол-во  [L]", self)
        set_settings_button_big(self.edit_quantity_button, self.presenter.open_quantity_dialog, is_enable=False)

        self.delete_button = QPushButton("Удалить товар  [D]", self)
        set_settings_button_big(self.delete_button,self.presenter.delete_selected_product,is_enable=False)

        self.add_product_button = QPushButton( "Добавить / Обновить товар  [A]", self)
        set_settings_button_big(self.add_product_button,self.presenter.open_product_dialog)

        self.pay_button2 = QPushButton("Оплата вручную  [R]", self)
        set_settings_button_big(self.pay_button2, self.presenter.open_manual_payment_dialog)

        self.last_action = QPushButton("История операций  [T]", self)
        set_settings_button_big(self.last_action, self.presenter.open_last_action_dialog)

        self.print_barcode_button = QPushButton("Печать штрих-кода  [K]", self)
        set_settings_button_big(self.print_barcode_button, self.presenter.open_barcode_print_dialog)

    # --------------------------------------------------
    # Изменение количества товара
    # --------------------------------------------------

    def change_quantity(self, delta):
        try:
            model = self.main_window.left_panel.product_model
            row = model.get_selected_row()

            if row is None:
                return

            product = model.get_product_by_row(row)
            if product is None:
                return

            product.update_quantity(delta)
            model.dataChanged.emit(model.index(row, 3), model.index(row, 4))

            self.presenter.update_total()
            self.main_window.left_panel.table_view.setFocus()

        except Exception as error:
            print(f"Ошибка изменения количества: {error}")

    def increment_quantity(self):
        self.change_quantity(+1)

    def decrement_quantity(self):
        self.change_quantity(-1)