from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QDoubleSpinBox, QPushButton, QLabel,
    QHBoxLayout, QSizePolicy, QWidget, QMessageBox, QCheckBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
from view.dialog.password_dialog import PasswordDialog
from PyQt5.QtGui import QKeyEvent
from view.dialog.product_history.utils import format_decimal_to_str
from search_global import create_search_result_list, POSITION_CONFIG, update_results, select_current_item, get_product_and_handle


class ProductDialog(QDialog):
    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить / Обновить товар")
        self.setFixedSize(1200, 700)
        self.db = db  # Ссылка на базу данных, чтобы найти товар
        self.product = None  # Будет хранить найденный товар
        self.font_size_label = 24


        self.layout = QVBoxLayout(self)


        # Кнопки переключения режимов
        self.mode_layout = QHBoxLayout()

        self.add_button = QPushButton("Добавить товар")
        self.update_button = QPushButton("Обновить товар")
        self.clear_button = QPushButton("Списать товар")
        self.union_button = QPushButton("Объеденить товар")


        self.add_button.setCheckable(True)
        self.update_button.setCheckable(True)
        self.clear_button.setCheckable(True)
        self.union_button.setCheckable(True)
        self.add_button.setChecked(True)


        self.add_button.clicked.connect(lambda: self.toggle_mode("add"))
        self.update_button.clicked.connect(lambda: self.toggle_mode("update"))
        self.clear_button.clicked.connect(lambda: self.toggle_mode("clear"))
        self.union_button.clicked.connect(lambda: self.toggle_mode("union"))


        self.mode_layout.addWidget(self.add_button, 45)
        self.mode_layout.addSpacing(10)
        self.mode_layout.addWidget(self.update_button, 45)
        self.mode_layout.addWidget(self.union_button, 45)
        self.mode_layout.addWidget(self.clear_button, 45)


        self.layout.addLayout(self.mode_layout)


        # Widget для добавления товара
        def add_widget_add_product():
            # Форма
            self.form_layout = QVBoxLayout()
            self.form_widget = QWidget()
            self.form_widget.setLayout(self.form_layout)

            def create_name_edit():
                label = QLineEdit(self)
                label.setPlaceholderText("Введите наименование ...")
                return label

            def create_barcode_edit():
                label = QLineEdit(self)
                label.setPlaceholderText("Введите или отсканируйте штрих-код ...")
                return label

            def create_multiple_barcode_edit():
                container = QHBoxLayout()
                self.label_main_barcode = QLabel("Штрих-коды товара (6 шт.):")
                self.label_main_barcode.setStyleSheet("font-size:30px;")
                self.label_text_barcode = QLabel()
                self.label_text_barcode.setStyleSheet("font-size:24px;")
                self.label_text_barcode.setWordWrap(True)

                self.label_main_barcode.setVisible(False)
                self.label_text_barcode.setVisible(False)


                container.addWidget(self.label_main_barcode)
                container.addWidget(self.label_text_barcode, alignment=Qt.AlignLeft)
                return container

            self.name_edit = create_name_edit()
            self.barcode_edit = create_barcode_edit()
            self.quantity_edit = self.create_quantity_edit()
            self.price_edit = self.create_price_edit()
            self.multiple_barcode = create_multiple_barcode_edit()


            self.form_layout.addLayout(self.multiple_barcode)
            self.form_layout.addStretch()
            self.form_layout.addLayout(self.create_labeled_input("Наименование товара:", self.name_edit))
            self.form_layout.addLayout(self.create_labeled_input("Штрих-код:", self.barcode_edit, True))
            self.button_add_product_barcode.clicked.connect(self.enter_add_barcode_add_product)
            self.form_layout.addLayout(self.create_labeled_input("Количество:", self.quantity_edit))
            self.form_layout.addLayout(self.create_labeled_input("Цена:", self.price_edit))

        # Widget для обновления товара
        def add_widget_udate_product():
            self.update_layout = QVBoxLayout()
            self.update_widget = QWidget()
            self.update_widget.setLayout(self.update_layout)

            # Create methods
            def create_update_search_layot():
                self.enter_pressed_from_list = [1]
                layot = QHBoxLayout()
                self.update_search_button = QPushButton("Поиск")
                self.update_search_barcode_edit = self.create_search_barcode_edit()
                self.update_search_barcode_edit.textChanged.connect(self.update_result_for_update_product)  # Автопоиск
                self.update_search_barcode_edit.returnPressed.connect(self.entered_update_barcode)
                self.update_search_button.clicked.connect(self.entered_update_barcode)

                layot.addWidget(self.update_search_barcode_edit)
                layot.addWidget(self.update_search_button)
                return layot

            def create_label_update(name, input_label, checkbox):
                style = self.get_style_fileds("on")
                input_label.setStyleSheet(style)
                input_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                checkbox.setMinimumHeight(input_label.sizeHint().height())

                container = QVBoxLayout()  # Основной вертикальный контейнер

                label = QLabel(name)  # Название сверху
                label.setStyleSheet(f"font-size:{self.font_size_label}px;")
                container.addWidget(label)

                input_layout = QHBoxLayout()  # Горизонтальный контейнер для input и чекбокса
                input_layout.setSpacing(30)

                input_layout.addWidget(input_label)

                input_layout.addWidget(checkbox)  # Выравниваем чекбокс по центру input
                # container.setAlignment(Qt.AlignTop)
                container.addLayout(input_layout)  # Добавляем горизонтальный блок в основной вертикальный контейнер
                return container

            def create_container_checkbox(name=""):
                checkbox = QCheckBox(name)
                checkbox.setChecked(False)
                style_checkbox = self.get_style_checkbox(True)
                checkbox.setStyleSheet(style_checkbox)

                # Создаем контейнер QWidget
                checkbox_widget = QWidget()

                # Используем QHBoxLayout
                layout = QHBoxLayout(checkbox_widget)
                layout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы
                layout.setSpacing(10)  # Настроим отступы между элементами

                # Добавляем чекбокс
                layout.addWidget(checkbox, alignment=Qt.AlignVCenter)

                return checkbox_widget

            def create_old_data_fields():
                style_label_old_data = "font-size:20px;margin-bottom:5px;margin-top:5px;color:black;font-weight:500;"

                self.old_quantity_label = QLabel("Количество на складе: ")
                self.old_price_label = QLabel("Старая цена: ")
                self.old_quantity_label.setStyleSheet(style_label_old_data)
                self.old_price_label.setStyleSheet(style_label_old_data)

                old_data_layout = QHBoxLayout()
                old_data_layout.addLayout(QVBoxLayout())
                old_data_layout2 = QVBoxLayout()
                old_data_layout2.addWidget(self.old_quantity_label)
                old_data_layout2.addWidget(self.old_price_label)
                old_data_layout.addLayout(old_data_layout2)
                return old_data_layout

            def create_fields():
                self.update_name_edit = QLineEdit(self)
                self.update_barcode_edit = QLineEdit(self)
                self.update_quantity_edit = self.create_quantity_edit()
                self.update_price_edit = self.create_price_edit()

            def create_checkboxes():
                self.update_name_chexbox_container = create_container_checkbox()
                self.update_barcode_chexbox_container = create_container_checkbox()
                self.update_quantity_chexbox_container = create_container_checkbox()
                self.update_price_chexbox_container = create_container_checkbox()

                self.update_name_chexbox = self.update_name_chexbox_container.findChild(QCheckBox)
                self.update_barcode_chexbox = self.update_barcode_chexbox_container.findChild(QCheckBox)
                self.update_quantity_chexbox = self.update_quantity_chexbox_container.findChild(QCheckBox)
                self.update_price_chexbox = self.update_price_chexbox_container.findChild(QCheckBox)

            #  Action methods
            def toggle_field_on_checkbox_change(checkbox, field_edit):
                """Метод для привязки состояния чекбокса к полю ввода"""
                is_True = True if checkbox.isChecked() else False
                style_var = "on" if checkbox.isChecked() else "off"
                field_edit.setEnabled(is_True)
                field_edit.setStyleSheet(self.get_style_fileds(style_var))

            def connect_checkboxes():
                """Подключает все чекбоксы к соответствующим полям."""
                # Для каждого чекбокса подключаем его изменение к методу toggle_field_on_checkbox_change
                def update_name_checkbox_changed():
                    """Обрабатывает изменение состояния чекбокса для имени."""
                    toggle_field_on_checkbox_change(self.update_name_chexbox, self.update_name_edit)

                def update_barcode_checkbox_changed():
                    """Обрабатывает изменение состояния чекбокса для штрих-кода."""
                    toggle_field_on_checkbox_change(self.update_barcode_chexbox, self.update_barcode_edit)

                def update_quantity_checkbox_changed():
                    """Обрабатывает изменение состояния чекбокса для количества."""
                    toggle_field_on_checkbox_change(self.update_quantity_chexbox, self.update_quantity_edit)

                def update_price_checkbox_changed():
                    """Обрабатывает изменение состояния чекбокса для цены."""
                    toggle_field_on_checkbox_change(self.update_price_chexbox, self.update_price_edit)

                self.update_name_chexbox.stateChanged.connect(update_name_checkbox_changed)
                self.update_barcode_chexbox.stateChanged.connect(update_barcode_checkbox_changed)
                self.update_quantity_chexbox.stateChanged.connect(update_quantity_checkbox_changed)
                self.update_price_chexbox.stateChanged.connect(update_price_checkbox_changed)


            self.result_list = []
            self.update_search_layout = create_update_search_layot()
            self.update_layout.addLayout(self.update_search_layout)
            self.result_list = create_search_result_list(
                self,
                self.update_search_barcode_edit,
            )
            self.result_list.itemClicked.connect(
                self.select_current_item_for_update
            )
            self.update_layout.addStretch()
            old_data_layout = create_old_data_fields()
            self.update_layout.addLayout(old_data_layout)
            self.update_layout.addStretch()
            create_fields()
            create_checkboxes()
            self.update_layout.addLayout(
                create_label_update(
                    "Наименование:",
                    self.update_name_edit,
                    self.update_name_chexbox_container,
                )
            )
            self.update_layout.addLayout(
                create_label_update(
                    "Штрих-код:",
                    self.update_barcode_edit,
                    self.update_barcode_chexbox_container,
                )
            )
            self.update_layout.addLayout(
                create_label_update(
                    "Добовляемое количество:",
                    self.update_quantity_edit,
                    self.update_quantity_chexbox_container,
                )
            )
            self.update_layout.addLayout(
                create_label_update(
                    "Новая цена:",
                    self.update_price_edit,
                    self.update_price_chexbox_container,
                )
            )
            connect_checkboxes()
            self.change_state_tab_inputs("off", "reload")
            self.toggle_old_labels(False)


        # Widget для списания товара
        def add_widget_clear_product():
            self.clear_layout = QVBoxLayout()
            self.clear_widget = QWidget()
            self.clear_widget.setLayout(self.clear_layout)

            def create_clear_search_layot():
                layot = QHBoxLayout()
                self.clear_flag_enter_list = [1]
                self.clear_search_button = QPushButton("Поиск")
                self.clear_search_barcode_edit = self.create_search_barcode_edit()

                self.clear_search_barcode_edit.returnPressed.connect(self.entered_button_search_clear)
                self.clear_search_button.clicked.connect(self.entered_button_search_clear)

                layot.addWidget(self.clear_search_barcode_edit)
                layot.addWidget(self.clear_search_button)
                return layot

            def create_clear_fields():
                self.clear_name_edit = QLineEdit(self)
                self.clear_barcode_edit = QLineEdit(self)
                self.clear_quantity_edit = self.create_quantity_edit()

            def create_old_clear_quantity_label():
                self.clear_layout.addStretch()
                style_label_old_data = "font-size:20px;margin-bottom:5px;margin-top:5px;color:black;font-weight:500;"
                self.old_clear_quantity_label = QLabel("Количество на складе: 100")
                self.old_clear_quantity_label.setStyleSheet(style_label_old_data)
                self.clear_layout.addWidget(self.old_clear_quantity_label)
                self.clear_layout.addStretch()

            self.clear_search_layot = create_clear_search_layot()
            self.clear_layout.addLayout(self.clear_search_layot)
            self.clear_list_search = create_search_result_list(self, self.clear_search_barcode_edit)
            self.clear_search_barcode_edit.textChanged.connect(self.update_result_for_clear_product)
            self.clear_list_search.itemClicked.connect(self.select_current_item_for_clear)

            create_old_clear_quantity_label()

            create_clear_fields()
            self.clear_layout.addLayout(self.create_labeled_input("Наименование:", self.clear_name_edit))
            self.clear_layout.addLayout(self.create_labeled_input("Штрих-код:", self.clear_barcode_edit))
            self.clear_layout.addLayout(self.create_labeled_input("Списываемое количество:", self.clear_quantity_edit))

            self.change_state_tab_inputs("off", "clear")
            self.old_clear_quantity_label.setVisible(False)

        # Widget для объединения товара
        def add_widget_union_product():
            self.union_layout = QVBoxLayout()
            self.union_widget = QWidget()
            self.union_widget.setLayout(self.union_layout)

            def create_union_fields():
                self.union_head_name_edit = self.create_search_barcode_edit()
                self.union_second_name_edit = self.create_search_barcode_edit()

            create_union_fields()

            self.union_list_search_header = create_search_result_list(self, self.union_head_name_edit)
            self.union_list_search_second = create_search_result_list(self, self.union_second_name_edit)

            self.union_head_name_edit.textChanged.connect(self.update_result_for_union_product_header)
            self.union_list_search_header.itemClicked.connect(self.select_current_item_for_union_header)
            self.union_head_name_edit.returnPressed.connect(self.entered_button_search_union_header)

            self.union_second_name_edit.textChanged.connect(self.update_result_for_union_product_second)
            self.union_second_name_edit.returnPressed.connect(self.entered_button_search_union_second)
            self.union_list_search_second.itemClicked.connect(self.select_current_item_for_union_second)

            def update_result_for_union_product():
                update_results(self.db, self.clear_search_barcode_edit, self.clear_list_search, **POSITION_CONFIG.get("product"))

            self.union_layout.addLayout(self.create_labeled_input("Основной товар:", self.union_head_name_edit))
            self.union_layout.addLayout(self.create_labeled_input("Добавляемый товар:", self.union_second_name_edit))
            self.union_layout.addStretch(1)

            # self.change_state_tab_inputs("off", "clear")

        # Кнопки действий
        def add_buttons_action():
            self.get_style_btn = lambda bck_clr: f"height:50px;color:white ;font-size:30px; " \
                                                 f"background-color:{bck_clr};border-radius: 10px;"
            self.button_layout = QHBoxLayout()
            self.save_button = QPushButton("Добавить")
            self.reset_button = QPushButton("Сброс")
            self.save_button.setStyleSheet(self.get_style_btn("#4CAF50"))
            self.reset_button.setStyleSheet(self.get_style_btn("#FF4D4D"))

            self.button_layout.addWidget(self.save_button)
            self.button_layout.addWidget(self.reset_button)
            self.layout.addLayout(self.button_layout)

            self.reset_button.clicked.connect(self.reset_all_fields)
            self.save_button.clicked.connect(self.save_product)


        add_widget_add_product()
        add_widget_udate_product()
        add_widget_clear_product()
        add_widget_union_product()

        self.layout.addWidget(self.form_widget)
        self.layout.addWidget(self.update_widget)
        self.layout.addWidget(self.union_widget)
        self.layout.addWidget(self.clear_widget)
        add_buttons_action()

        self.setLayout(self.layout)
        self.toggle_mode("add")


    # Fucntions for search products
    # For update product
    def entered_update_barcode(self, product_value=False):
        if len(self.enter_pressed_from_list) > 1:
            self.enter_pressed_from_list = [1]  # Сбрасываем флаг
            return  # Не выполняем действия, если Enter был на списке товаров

        get_product_and_handle(product_value, self.update_search_barcode_edit, self.db, self.succes_update)

    def succes_update(self, product):
        count = format_decimal_to_str(product[2])
        price = format_decimal_to_str(product[3])
        self.change_state_save_button(True)
        self.change_state_tab_inputs("on", "reload", False)
        self.update_name_edit.setText(product[1])
        self.update_barcode_edit.setText(product[0])

        self.old_quantity_label.setText(f"Количество на складе: {count} шт. (кг.)")
        self.old_price_label.setText(f"Старая цена: {price} ₽")

        self.toggle_old_labels(True)
        self.update_search_barcode_edit.setText("")
        self.update_search_barcode_edit.setFocus()

    def select_current_item_for_update(self):
        select_current_item(self.result_list, self.entered_update_barcode)

    def update_result_for_update_product(self):
        update_results(self.db, self.update_search_barcode_edit, self.result_list, **POSITION_CONFIG.get("product"))

    # For clear product
    def entered_button_search_clear(self, product_value=False):
        get_product_and_handle(product_value,self.clear_search_barcode_edit, self.db, self.succes_clear)

    def succes_clear(self, product):
        count = format_decimal_to_str(product[2])
        self.change_state_save_button(True)
        self.clear_name_edit.setText(product[1])
        self.clear_barcode_edit.setText(product[0])
        self.old_clear_quantity_label.setText(f"Количество на складе: {count} шт. (кг.)")
        self.change_state_tab_inputs("on", "clear")
        self.old_clear_quantity_label.setVisible(True)
        self.clear_search_barcode_edit.setText("")
        self.clear_search_barcode_edit.setFocus()

    def select_current_item_for_clear(self):
        select_current_item(self.clear_list_search, self.entered_button_search_clear)

    def update_result_for_clear_product(self):
        update_results(self.db, self.clear_search_barcode_edit,self.clear_list_search, **POSITION_CONFIG.get("product"))

    # For union product
    def entered_button_search_union_header(self, product_value=False):
        get_product_and_handle(product_value, self.union_head_name_edit, self.db, self.succes_union_header)

    def succes_union_header(self, product):
        count = format_decimal_to_str(product[2])
        price = product[3]
        text = f"{product[1]} - ( {price} руб. ) - ( {count} шт.(кг.) )"

        self.union_head_name_edit.setText(text)
        self.union_header_data = product

        style = self.get_style_fileds("off")
        self.union_head_name_edit.setStyleSheet(style)
        self.union_head_name_edit.setEnabled(False)

        style = self.get_style_fileds("on")
        self.union_second_name_edit.setStyleSheet(style)
        self.union_second_name_edit.setEnabled(True)

        self.union_second_name_edit.setText("")
        self.union_second_name_edit.setFocus()

    def entered_button_search_union_second(self, product_value=False):
        get_product_and_handle(product_value, self.union_second_name_edit, self.db, self.succes_union_second)

    def succes_union_second(self, product):
        count = format_decimal_to_str(product[2])
        price = format_decimal_to_str(product[3])
        text = f"{product[1]} - ( {price} руб. ) - ( {count} шт.(кг.) )"

        text_head = self.union_head_name_edit.text().strip()

        if text == text_head:
            QMessageBox.warning(self, "Ошибка", f"Продукт не может объединиться с самим собой!")
            self.union_second_name_edit.setText("")
            self.union_second_name_edit.setFocus()
            return

        self.union_second_data = product

        self.change_state_save_button(True)
        self.union_second_name_edit.setText(text)

        style = self.get_style_fileds("off")
        self.union_second_name_edit.setStyleSheet(style)
        self.union_second_name_edit.setEnabled(False)

    def select_current_item_for_union_header(self):
        select_current_item(self.union_list_search_header, self.entered_button_search_union_header)

    def select_current_item_for_union_second(self):
        select_current_item(self.union_list_search_second, self.entered_button_search_union_second)

    def update_result_for_union_product_header(self):
        update_results(self.db, self.union_head_name_edit,self.union_list_search_header, **POSITION_CONFIG.get("product"))

    def update_result_for_union_product_second(self):
        update_results(self.db, self.union_second_name_edit, self.union_list_search_second, **POSITION_CONFIG.get("product"))

    # --------------------------------------------------------------------------------------

    def enter_add_barcode_add_product(self):
        old_text = self.label_text_barcode.text()
        text = self.barcode_edit.text()


        def check_valid_in_old_text(text):
            new_list = old_text.split(";")
            if text in new_list:
                return True

        def check_valid_data_text(text):
            if not text.isdigit():
                return True

        if not text:
            QMessageBox.warning(self, "Ошибка", "Поле должны быть заполнено!")
            return

        if self.db.barcode_exists(text):
            QMessageBox.warning(self, "Ошибка", "Данный штрих-код уже используется!")
            self.barcode_edit.setFocus()
            return

        if check_valid_in_old_text(text):
            QMessageBox.warning(self, "Ошибка", "Данный штрих-код уже добавлен в поле!")
            self.barcode_edit.setFocus()
            return


        if check_valid_data_text(text):
            QMessageBox.warning(self, "Ошибка", "Некоректный штрих-код!")
            self.barcode_edit.setFocus()
            return


        if not old_text:
            old_text = ""
        else:
            old_text = f"{old_text};"

        self.label_text_barcode.setText(f"{old_text}{text}")

        self.barcode_edit.setText("")
        self.barcode_edit.setFocus()

        count_barcodes = self.label_text_barcode.text().split(';')


        self.label_main_barcode.setText(f"Штрих-коды товара ({len(count_barcodes)} шт.):")


        QMessageBox.information(self, "Успех", f"Штрих-код: {text} добавлен к товару!")
        self.label_main_barcode.setVisible(True)
        self.label_text_barcode.setVisible(True)

        # self.barcode_edit = create_barcode_edit()
        # self.multiple_barcode = create_multiple_barcode_edit()

    # KeyPressMethod
    def keyPressEvent(self, event: QKeyEvent):
        """⏬ Обрабатываем нажатия клавиш для перемещения по списку"""
        try:
            return_value = False

            def change_set_number(button, list_data, input_field, method, is_enter_value):
                nonlocal return_value  # Используем переменную из внешней области
                if button.isChecked():
                    if list_data.isVisible() and list_data.count() > 0:
                        current_row = list_data.currentRow()

                        if event.key() == Qt.Key_Down:  # Стрелка вниз
                            if current_row == -1:
                                list_data.setCurrentRow(0)
                                list_data.setFocus()
                                return_value = True

                        elif event.key() == Qt.Key_Up:  # Стрелка вверх
                            if current_row == 0:
                                list_data.setCurrentRow(-1)
                                input_field.setFocus()
                                return_value = True

                        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):  # Нажатие Enter
                            try:
                                method()
                                is_enter_value.append(1)
                            except Exception as a:
                                print(a)

            # Проверяем кнопки обновления/списания товара
            if self.update_button.isChecked():
                change_set_number(self.update_button, self.result_list, self.update_search_barcode_edit,
                                  self.select_current_item_for_update, self.enter_pressed_from_list)

            if self.clear_button.isChecked():
                change_set_number(self.clear_button, self.clear_list_search, self.clear_search_barcode_edit,
                                  self.select_current_item_for_clear, self.clear_flag_enter_list)

            # 🔹 Обработка Backspace, если фокус на списке
            focused_widget = self.focusWidget()
            if event.key() == Qt.Key_Backspace and isinstance(focused_widget, QListWidget):
                self.update_search_barcode_edit.setFocus()  # Переключаем фокус в поле ввода
                cursor_pos = self.update_search_barcode_edit.cursorPosition()
                text = self.update_search_barcode_edit.text()
                self.update_search_barcode_edit.setText(text[:cursor_pos - 1] + text[cursor_pos:])  # Удаляем символ
                self.update_search_barcode_edit.setCursorPosition(cursor_pos - 1)
                return  # Завершаем обработку, не передавая событие дальше

            if return_value:
                return

            super().keyPressEvent(event)  # Передаём событие дальше

        except Exception as a:
            print(a)

    # Method for create elements
    def create_labeled_input(self, label_text, input_widget, is_barcode=False):
        input_widget.setStyleSheet(self.get_style_fileds())
        container = QVBoxLayout()
        input_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        label = QLabel(label_text)
        label.setStyleSheet(f"font-size:{self.font_size_label}px;")  # Уменьшаем отступ между меткой и полем
        container.addWidget(label)
        if not is_barcode:
            container.addWidget(input_widget)
        if is_barcode:
            # Горизонтальный контейнер
            h_layout = QHBoxLayout()

            self.button_add_product_barcode = QPushButton("+")
            self.button_add_product_barcode.setFixedSize(40, 40)
            self.button_add_product_barcode.setStyleSheet("""
                QPushButton {
                    background-color: #01B4E4;
                    color: white;
                    font-size: 30px;
                    font-weight: bold;
                    border-radius: 20px;
                }
                QPushButton:hover {
                    font-size:32px;
                }
            """)
            h_layout.addWidget(input_widget)
            h_layout.addWidget(self.button_add_product_barcode, alignment=Qt.AlignTop)
            container.addLayout(h_layout)

        container.setAlignment(Qt.AlignCenter)
        return container

    def create_quantity_edit(self, value=1):
        label = QDoubleSpinBox(self)
        label.setMinimum(0.01)
        label.setMaximum(99999.99)
        label.setSuffix(" шт. (кг.)")
        label.setValue(value)
        return label

    def create_price_edit(self, price=1):
        label = QDoubleSpinBox(self)
        label.setValue(price)
        label.setSuffix(" ₽")
        label.setMinimum(0.01)
        label.setMaximum(99999.99)
        label.setDecimals(2)
        label.setStyleSheet("font-size:18px;margin-bottom:40px;")
        return label

    def create_search_barcode_edit(self):
        class BarcodeLineEdit(QLineEdit):
            def keyPressEvent(self, event):
                if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                    self.returnPressed.emit()  # Явно вызываем сигнал returnPressed
                    return  # Предотвращаем передачу события дальше
                super().keyPressEvent(event)

        label = BarcodeLineEdit(self)
        label.setPlaceholderText("Введите или отсканируйте штрих-код ...")
        label.setStyleSheet("height: 40px; font-size:24px; border-radius: 10px; padding-left:5px; "
                            "border: 1px solid black;")
        return label
    # ----------------------------------------------------------------

    # Header methods
    def toggle_mode(self, mode):
        if mode == "add":
            self.add_button.setChecked(True)
            self.update_button.setChecked(False)
            self.clear_button.setChecked(False)
            self.union_button.setChecked(False)

            self.save_button.setText("Добавить")
            self.set_color_bcgnd(self.add_button, self.update_button, self.clear_button,self.union_button)
            self.name_edit.setFocus()

            self.form_widget.show()
            self.update_widget.hide()
            self.clear_widget.hide()
            self.union_widget.hide()

        if mode == "update":
            self.add_button.setChecked(False)
            self.update_button.setChecked(True)
            self.clear_button.setChecked(False)
            self.union_button.setChecked(False)

            self.save_button.setText("Обновить")
            self.set_color_bcgnd(self.update_button, self.add_button,  self.clear_button,self.union_button)
            self.update_search_barcode_edit.setFocus()

            self.form_widget.hide()
            self.update_widget.show()
            self.clear_widget.hide()
            self.union_widget.hide()

        if mode == "clear":
            self.password_dialog = PasswordDialog()
            if self.password_dialog.exec_():
                self.add_button.setChecked(False)
                self.update_button.setChecked(False)
                self.clear_button.setChecked(True)
                self.union_button.setChecked(False)

                self.save_button.setText("Списать")
                self.set_color_bcgnd(self.clear_button, self.add_button, self.update_button, self.union_button)
                self.clear_search_barcode_edit.setFocus()

                self.form_widget.hide()
                self.update_widget.hide()
                self.clear_widget.show()
                self.union_widget.hide()

        if mode == "union":
            self.union_button.setChecked(True)
            self.add_button.setChecked(False)
            self.update_button.setChecked(False)
            self.clear_button.setChecked(False)

            self.save_button.setText("Объеденить")
            self.set_color_bcgnd(self.union_button, self.add_button, self.update_button, self.clear_button)

            self.union_widget.show()
            self.form_widget.hide()
            self.update_widget.hide()
            self.clear_widget.hide()

        self.reset_all_fields()

    def save_product(self):
        """Обработчик нажатия кнопки 'Добавить/Обновить/Списать'"""
        if self.add_button.isChecked():
            self.add_product()
        elif self.update_button.isChecked():
            self.update_product()
        elif self.clear_button.isChecked():
            self.clear_product()
        elif self.union_button.isChecked():
            self.union_products()

    def add_product(self):
        """Добавление нового товара"""
        name = self.name_edit.text().strip()
        barcode = self.barcode_edit.text().strip()
        quantity = self.quantity_edit.value()
        price = self.price_edit.value()

        raw_multiple_barcode = self.label_text_barcode.text().split(";")

        def check_barcodes():
            if raw_multiple_barcode[0] == "":
                return False
            return True


        multiple_barcode = raw_multiple_barcode if check_barcodes() else [barcode]


        try:
            if not name or quantity <= 0 or price <= 0 or not multiple_barcode:
                QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены и содержать корректные данные!")
                self.name_edit.setFocus()
                return


            check_name = self.db.get_product_id_by_name(name)

            if check_name:
                QMessageBox.warning(self, "Ошибка", f"Товар с наименованием {name} уже имеется в базе данных")
                self.name_edit.setFocus()
                return

            if barcode:
                check_barcode = self.db.get_product_by_barcode(barcode)
                if check_barcode:
                    QMessageBox.warning(self, "Ошибка", f"Товар со штрих-кодом {barcode} уже имеется в базе данных")
                    self.barcode_edit.setFocus()
                    return


            # Здесь можно добавить логику записи в базу данных
            result_db = self.db.add_new_product(multiple_barcode, name, price, quantity)
            if result_db:
                QMessageBox.information(self, "Успех", f"Товар '{name}' добавлен!")
                self.reset_all_fields()
                self.name_edit.setFocus()
                return
            else:
                QMessageBox.warning(self, "Ошибка", f"Произошла ошибка при добавлении товара в базу данных")
                self.name_edit.setFocus()
                return
        except Exception as a:
            print(a)

    def update_product(self):
        """Обновление информации о товаре"""
        barcode_list = self.update_barcode_edit.text().strip().split(";")
        barcode = barcode_list[0] if barcode_list[0] else barcode_list[1]
        try:
            # Проверяем, какие поля обновляются
            updates = {}
            if self.update_name_chexbox.isChecked():
                updates['name'] = self.update_name_edit.text().strip()
            if self.update_barcode_chexbox.isChecked():
                updates['barcode'] = self.update_barcode_edit.text().strip()
            if self.update_quantity_chexbox.isChecked():
                updates['quantity'] = self.update_quantity_edit.value()
            if self.update_price_chexbox.isChecked():
                updates['price'] = self.update_price_edit.value()

            if not updates:
                QMessageBox.warning(self, "Ошибка", "Выберите хотя бы одно поле для обновления!")
                self.update_search_barcode_edit.setFocus()
                return

            result = self.db.update_all_fields(barcode,updates)

            if result:
                QMessageBox.information(self, "Успех", f"Товар {barcode} обновлен!")
                self.reset_all_fields()
                self.update_search_barcode_edit.setFocus()
                return
            else:
                QMessageBox.warning(self, "Ошибка", "Ошибка при обновлении товара")
                self.reset_all_fields()
                self.update_search_barcode_edit.setFocus()
                return

        except Exception as a:
            print(a)

    def clear_product(self):
        """Списание товара"""
        try:
            barcode = self.clear_barcode_edit.text().strip()
            quantity_to_remove = self.clear_quantity_edit.value()

            # Логика поиска товара (псевдо-код)
            self.product = self.db.get_product_by_barcode(barcode) # (barcode, name, quantity, price_sale)
            product_id = self.product[-1]

            if  float(quantity_to_remove) > float(self.product[2]):
                QMessageBox.warning(self, "Ошибка", "Списываемое количество не может превышать количество находящихся на складе!")
                self.clear_quantity_edit.setValue(self.product[2])
                self.clear_quantity_edit.setFocus()
                return

            resuls = self.db.clear_quantity_product(product_id, quantity_to_remove)
            if resuls:
                QMessageBox.information(self, "Успех", f"У {resuls} cписано {quantity_to_remove} единиц товара!")
                self.reset_all_fields()
                return
            else:
                QMessageBox.warning(self, "Ошибка", "Ошибка при cписании товара в базе данных")
                self.clear_search_barcode_edit.setFocus()
                return
        except Exception as a:
            print(a)

    def confirm_merge(self, main_product_id, secondary_product_id):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Подтверждение объединения")
        msg_box.setText(
            f"Вы уверены, что хотите объединить товар <<{secondary_product_id}>> с товаром <<{main_product_id}>>?"
        )
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setIcon(QMessageBox.Warning)
        result = msg_box.exec_()

        return result == QMessageBox.Yes

    def union_products(self):
        # (barcode, name, quantity, price_sale, id)
        header_data = self.union_header_data
        second_data = self.union_second_data


        old_name = second_data[1]
        old_barcode = second_data[0]
        old_quantity = second_data[2]
        old_price = second_data[3]
        old_id = second_data[4]

        text_old = f"{old_name} ( {old_price} руб. ) ( {old_quantity} шт.(кг.) ) (id {old_id})"


        main_id = header_data[4]
        second_id = second_data[4]

        add_quantity = float(old_quantity)

        if self.confirm_merge(header_data[1], old_name):
            success = self.db.merge_products(main_id, second_id, add_quantity, union_data=text_old)
            if success:
                QMessageBox.information(self, "Успешно", "Товары успешно объединены!")
            else:
                QMessageBox.critical(self, "Ошибка", "Ошибка при объединении товаров.")
        else:
            QMessageBox.information(self, "Отмена", "Объединение отменено.")

        self.reset_all_fields()

    def reset_all_fields(self):
        """Сбрасывает все поля во всех вкладках"""
        try:
            current_tab = self.save_button.text()
            # Сброс полей вкладки 'Добавить'
            self.name_edit.clear()
            self.barcode_edit.clear()
            self.quantity_edit.setValue(1)
            self.price_edit.setValue(1)
            self.label_main_barcode.setVisible(False)
            self.label_text_barcode.setVisible(False)
            self.label_main_barcode.setText("")
            self.label_text_barcode.setText("")

            # Сброс полей вкладки 'Обновить'
            self.update_search_barcode_edit.clear()
            self.update_barcode_edit.clear()
            self.update_name_edit.clear()
            self.update_quantity_edit.setValue(1)
            self.update_price_edit.setValue(1)

            # Сброс чекбоксов во вкладке 'Обновить'
            self.update_name_chexbox.setChecked(False)
            self.update_barcode_chexbox.setChecked(False)
            self.update_quantity_chexbox.setChecked(False)
            self.update_price_chexbox.setChecked(False)
            self.change_state_tab_inputs("off","reload")

            # # Сброс меток во вкладке 'Обновить'
            self.old_quantity_label.setText("Количество на складе: -")
            self.old_price_label.setText("Старая цена: -")
            self.toggle_old_labels(False)


            # Сброс полей вкладки 'Списать'
            self.clear_name_edit.clear()
            self.clear_barcode_edit.clear()
            self.clear_quantity_edit.setValue(1)
            self.old_clear_quantity_label.setVisible(False)
            self.change_state_tab_inputs("off", "clear")


            # Cброс полей в Объеденить
            style_on = self.get_style_fileds("on")
            style_off = self.get_style_fileds("off")

            self.union_head_name_edit.setStyleSheet(style_on)
            self.union_head_name_edit.setEnabled(True)
            self.union_head_name_edit.setText("")

            self.union_second_name_edit.setStyleSheet(style_off)
            self.union_second_name_edit.setEnabled(False)
            self.union_second_name_edit.setText("")


            if current_tab ==  "Обновить":
                self.update_search_barcode_edit.setFocus()
                self.change_state_save_button(False)
            if current_tab ==  "Списать":
                self.clear_search_barcode_edit.setFocus()
                self.change_state_save_button(False)
            if current_tab == "Добавить":
                self.name_edit.setFocus()
                self.change_state_save_button(True)

            if current_tab == "Объеденить":
                self.change_state_save_button(False)
                self.union_head_name_edit.setFocus()


        except Exception as a:
            print(a)

    def change_state_save_button(self, is_Enabled):
        style = "#4CAF50" if is_Enabled else "#D6DADF"
        self.save_button.setStyleSheet(self.get_style_btn(style))
        self.save_button.setEnabled(is_Enabled)

    # Set style elements
    def get_style_checkbox(self, mode):
        bckgnd = "white" if mode else "#D6DADF"
        style_inner = f"QCheckBox::indicator {{ width: 38px; height: 38px;" \
                      f"border-radius: 5px;border: 1px solid #555;background-color: {bckgnd};}}" \
                      f"QCheckBox::indicator:checked {{background: #76B9ED;border: 1px solid black;}}" \
                      f"QCheckBox {{margin-bottom: 7px;}}"
        return style_inner

    def get_style_fileds(self, action="on"):
        bckgnd_cld = "white" if action == "on" else "#D6DADF"
        clr = "black" if action == "on" else "#aaa"
        style = f"font-size:22px; padding-left:5px; margin-bottom:7px;" \
                f"height:40px; border-radius:10px; border: 1px solid black; " \
                f"background-color: {bckgnd_cld}; color: {clr};"
        return style

    def set_color_bcgnd(self, button_enter, button_off, button_off2, button_off3):
        def style_btn(color):
            return f"height:50px;color:black ;font-size:30px; background-color:{color};border-radius: 10px;border: 1px solid black;"

        bck_color_btn_off = "white"
        bck_color_btn_on = "#76B9ED"
        button_enter.setStyleSheet(style_btn(bck_color_btn_on))
        button_off.setStyleSheet(style_btn(bck_color_btn_off))
        button_off2.setStyleSheet(style_btn(bck_color_btn_off))
        button_off3.setStyleSheet(style_btn(bck_color_btn_off))
    # ------------------------------------------------------------------

    def change_state_tab_inputs(self, mode, tabs, global_mode=True):
        """Блокирует все элементы на вкладке 'Обновить товар', включая поля ввода и чекбоксы."""
        style = self.get_style_fileds(mode)
        is_True = True if mode == "on" else False

        def set_change_element(element):
            style_inner = self.get_style_checkbox(is_True) if isinstance(element, QCheckBox) else style
            element.setEnabled(is_True)
            element.setStyleSheet(style_inner)

        def set_fields():
            if tabs == "reload":
                set_change_element(self.update_name_edit)
                set_change_element(self.update_barcode_edit)
                set_change_element(self.update_quantity_edit)
                set_change_element(self.update_price_edit)
            else:
                if not is_True:
                    set_change_element(self.clear_name_edit)
                    set_change_element(self.clear_barcode_edit)
                set_change_element(self.clear_quantity_edit)


        def set_checkbox():
            set_change_element(self.update_name_chexbox)
            set_change_element(self.update_barcode_chexbox)
            set_change_element(self.update_quantity_chexbox)
            set_change_element(self.update_price_chexbox)

        if global_mode:
            set_fields()
            set_checkbox()
        else:
            set_checkbox()

    def toggle_old_labels(self, visible):
        self.old_quantity_label.setVisible(visible)
        self.old_price_label.setVisible(visible)



