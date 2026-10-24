from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem, QWidget,
    QLabel, QVBoxLayout, QGridLayout,QHBoxLayout
)
from PyQt5.QtGui import QBrush, QColor, QFont
from app.view.dialog.product_history.tabs.history_tab.calculator.daily_statistic import get_statistic_fields


def create_history_tab(dialog):

    dialog.tab_changes = QTreeWidget()
    dialog.tabs.addTab(dialog.tab_changes, "История операций")
    set_settings_history_tab(dialog)
    header = dialog.tab_changes.header()
    header.setDefaultAlignment(Qt.AlignCenter)

def set_count_column(dialog):
    dialog.tab_changes.setColumnCount(8)  # Добавляем два скрытых столбца для id_sale и id_change_inventory
    dialog.tab_changes.setHeaderLabels(
        ["Действие", "Тип продажи", "Сумма операции", "Кол-во товаров", "Время", "sale_id", "change_id", "is_date"]
    )

def set_style_culumn(dialog):
    dialog.tab_changes.setStyleSheet("""
    QHeaderView::section {
        font-weight: bold;
        font-size: 11pt;} 
    QTreeView::item { 
        height: 36px; 
        padding: 1px;
        }
    QTreeView::item:has-children {
        border-right: 1px solid black;
        border-bottom: 1px solid black;
        border-top: 1px solid black;
    }
    QTreeView::item:selected {
        background-color: #d0eaff;
        color: black;
    }
    QTreeView::item:selected:active {
        background-color: #a0d0ff;
    }
    QTreeView::item:focus {
        outline: none;
        
    }
    QTreeView::item:selected:active {
        outline: none;
    }
    """)

    # Устанавливаем шрифт
    font = QFont()
    font.setPointSize(14)  # Размер шрифта
    dialog.tab_changes.setFont(font)
    dialog.tab_changes.setFixedWidth(1369)

def set_column_width(dialog):
    # Ширина колонок
    dialog.tab_changes.setColumnWidth(0, 300)
    dialog.tab_changes.setColumnWidth(1, 400)
    dialog.tab_changes.setColumnWidth(2, 200)
    dialog.tab_changes.setColumnWidth(3, 200)
    dialog.tab_changes.setColumnWidth(4, 200)  # Увеличиваем ширину "Время"

    dialog.tab_changes.setColumnHidden(5, True)  # Скрытый столбец для sale_id
    dialog.tab_changes.setColumnHidden(6, True)  # Скрытый столбец для change_id
    dialog.tab_changes.setColumnHidden(7, True)  # Скрытый столбец для is_date



def set_action_row(dialog):
    # Запрещаем редактирование и выделение
    dialog.tab_changes.setEditTriggers(QTableWidget.NoEditTriggers)
    dialog.tab_changes.setSelectionMode(QTableWidget.NoSelection)

    # Устанавливаем поведение выделения строк
    dialog.tab_changes.setSelectionBehavior(QTableWidget.SelectRows)
    dialog.tab_changes.setSelectionMode(QTableWidget.SingleSelection)  # Одинарное выделение
    dialog.tab_changes.setEditTriggers(QTableWidget.NoEditTriggers)  # Запрещаем редактирование таблицы

def set_settings_history_tab(dialog):
    set_count_column(dialog)
    set_style_culumn(dialog)
    set_column_width(dialog)
    set_action_row(dialog)

#-------------------------------------
def create_tree_item(text=None, data_dict=None):
    value = text

    if isinstance(text, list | tuple):
        value = list(map(str, text))
    item = QTreeWidgetItem(value)

    if data_dict:
        item.setData(0, Qt.UserRole, data_dict)

    if value:
        for i in range(len(value)):
            item.setTextAlignment(i, Qt.AlignCenter)
    return item

def get_data_dict_in_tree_item(item):
    return item.data(0, Qt.UserRole)

def set_settings_header_cell(item):
    font = QFont('Arial', 16)
    brush_foreground = QBrush(QColor(255, 255, 255))  # Белый текст
    brush_background = QBrush(QColor(100, 100, 100))  # Серый фон

    column_count = item.columnCount()
    for col in range(column_count):
        item.setFont(col, font)
        item.setForeground(col, brush_foreground)
        item.setBackground(col, brush_background)

def create_date_three_item(date):
    date_item = create_tree_item([date], {"day": date})
    set_settings_header_cell(date_item)
    return date_item


def create_custom_cell_widget(sub_items: list, is_union=False):
    outer_container = QWidget()
    outer_container.setObjectName("customContainer")

    inner_container = QWidget()
    inner_container.setObjectName("innerContent")

    outer_layout = QVBoxLayout(outer_container)
    outer_layout.setContentsMargins(260, 4, 250, 10)
    outer_layout.addWidget(inner_container)

    main_layout = QVBoxLayout(inner_container)
    main_layout.setContentsMargins(0, 0, 0, 0)
    # main_layout.setSpacing(12)

    # === Таблица с данными ===
    grid = QGridLayout()
    # grid.setHorizontalSpacing(40)
    # grid.setVerticalSpacing(12)
    grid.setColumnStretch(0, 3)  # "Наименование" — широкий
    grid.setColumnStretch(1, 1)  # "Количество" — узкий
    grid.setColumnStretch(2, 1)  # "Цена" — узкий

    # Заголовки
    headers = ["Наименование", "Количество", "Цена" if not is_union else "Информация"]
    for col, title in enumerate(headers):
        lbl = QLabel(title)
        lbl.setObjectName("customTitle")
        if col != 0:
            lbl.setAlignment(Qt.AlignCenter)
        else:
            lbl.setAlignment(Qt.AlignLeft)
        grid.addWidget(lbl, 0, col)

    # Данные
    for row_index, row_data in enumerate(sub_items, start=1):
        for col, value in enumerate(row_data):
            lbl = QLabel(value)
            lbl.setObjectName("customLabel")
            if col != 0:
                lbl.setAlignment(Qt.AlignCenter)
            else:
                lbl.setAlignment(Qt.AlignLeft)
            grid.addWidget(lbl, row_index, col)

    main_layout.addLayout(grid)

    # Стили
    outer_container.setStyleSheet("""
        QWidget#innerContent {
            background-color: #e3e3e3;
            border-radius: 6px;
            font-size: 20px;
        }
        
        QWidget#customContainer {
        }

        QLabel#customTitle {
            font-weight: bold;
            font-size: 12pt;
            padding-top: 7px;
        }

        QLabel#customLabel {
            font-size: 10pt;
            color: #333;
            padding-bottom: 7px;
        }
    """)

    return outer_container


def create_details_widget(dialog):
    def get_style_for_table_main():
        style = """
            QTableWidget {
                background-color: #f0f0f0;  /* Светло-серый фон */
                border: none;
                border-radius: 5px;
                font-size:20px;
            }
        """
        return style

    def get_style_for_horizontal_table():
        style = """
            QHeaderView::section {
                background-color: #f0f0f0;  /* Светло-серый фон */
                border: none;
                font-weight: bold;
            }
        """
        return style

    dialog.details_widget = QWidget(dialog)
    dialog.details_widget.setStyleSheet("background-color: #f0f0f0; border: 2px solid black; border-radius:5px;")
    dialog.details_widget.setGeometry(0, 0, 998, 500)  # Стартовые размеры
    dialog.details_widget.hide()

    # Заголовок информации
    dialog.details_label = QLabel("Подробная информация", dialog.details_widget)
    dialog.details_label.setStyleSheet("background-color: #f0f0f0;border:none; font-size:20px;text-align: centr;")
    dialog.details_label.setGeometry(10, 5, 993, 20)  # widget.setGeometry(x, y, width, height)
    dialog.details_label.setAlignment(Qt.AlignCenter)

    # Создаем QTableWidget для отображения деталей
    dialog.details_table = QTableWidget(dialog.details_widget)
    dialog.details_table.setGeometry(10, 30, 993, 500)
    dialog.details_table.setColumnCount(4)
    dialog.details_table.setHorizontalHeaderLabels(["Название", "Количество", "Цена", "Общая сумма"])
    dialog.details_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Запрещаем редактирование
    dialog.details_table.setSelectionMode(QTableWidget.NoSelection)  # Запрещаем выделение
    dialog.details_table.verticalHeader().setVisible(False)  # Убираем индексы строк
    dialog.details_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # Показывать скролл
    dialog.details_table.setMaximumHeight(600)  # Максимальная высота, после которой скролл

    # Устанавливаем ширину колонок перед режимом изменения
    dialog.details_table.setColumnWidth(0, 653)  # "Название"
    dialog.details_table.setColumnWidth(1, 110)  # "Количество"
    dialog.details_table.setColumnWidth(2, 110)  # "Цена"
    dialog.details_table.setColumnWidth(3, 110)  # "Общая сумма"

    # Устанавливаем режим изменения размеров колонок
    dialog.details_table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

    # Применяем стили
    dialog.details_table.setStyleSheet(get_style_for_table_main())
    dialog.details_table.horizontalHeader().setStyleSheet(get_style_for_horizontal_table())

    # Принудительно обновляем виджет
    dialog.details_table.updateGeometry()

def create_date_first_line(dialog):
    row_height = 35
    dialog.date_widget_first_line = QWidget(dialog)
    dialog.date_widget_first_line.setStyleSheet("background-color: #646464;color:white;")
    dialog.date_widget_first_line.setGeometry(41, 103, 1321, row_height)  # Стартовые размеры x,y,width,height
    dialog.date_widget_first_line.show()

    # Метка для отображения даты (вместо первой таблицы)
    dialog.date_label_first_line = QLabel("", dialog.date_widget_first_line)  # Динамическая дата
    dialog.date_label_first_line.setAlignment(Qt.AlignCenter)
    dialog.date_label_first_line.setFont(QFont('Arial', 16))

    # Определяем высоту строки как у таблицы
    dialog.date_label_first_line.setGeometry(0, 0, 1321, row_height)  # x, y, width, height
    dialog.date_widget_first_line.raise_()
    dialog.date_label_first_line.raise_()

def _create_comboBox(dialog, start, table):
    table.setSpan(start + 1, 0, 1, 3)
    combo = QComboBox()
    combo.setStyleSheet("""
        QComboBox {
            background-color: white;  /* цвет фона */
            color: black;             /* цвет текста */
            font-size: 22px;            /* размер шрифта */
            font-weight: bold;
        }
        QComboBox QAbstractItemView {
            background-color: white;    /* фон выпадающего списка */
            color: black;               /* цвет текста в списке */
            selection-background-color: #01B4E4; /* цвет подсветки выбранного */
        }
    """)
    combo.setEditable(True)
    combo.lineEdit().setAlignment(Qt.AlignCenter)
    combo.lineEdit().setReadOnly(True)
    table.setCellWidget(start + 1, 1, combo)
    return combo

def create_right_panel_info(dialog):
    try:
        table = QTableWidget(dialog)
        table.setColumnCount(3)
        # table.setGeometry(1358, 65, 522, 972)  # x,
        table.setGeometry(1385, 65, 522, 972) #

        # Добавим 4 строки для примера
        table.setRowCount(26)

        def create_item(text):
            item = QTableWidgetItem(text)
            item.setFont(QFont('Arial', 14, QFont.Bold))
            item.setBackground(QColor(227, 227, 227))  # цвет фона
            item.setTextAlignment(Qt.AlignCenter)
            return item


        def create_data_and_insert(start):
            def create_item_no_bold(text):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                item.setBackground(QColor(227, 227, 227))
                item.setFont(QFont("Arial", 12))
                item.setForeground(QColor(0, 0, 0))
                return item

            for i, statistic_field in enumerate(get_statistic_fields()):
                row = start + i

                for col in range(3):
                    text = statistic_field.metadata["label"] if col == 0 else "-"

                    table.setItem(row, col, create_item_no_bold(text))

        def create_data_header_section_and_insert(row):
            lst=["Действие","Кол-во","Сумма"]
            for i in range(0,3):
                item = create_item(lst[i])
                table.setItem(row,i,item)

        def create_day_data(start):
            table.setSpan(start, 0, 1, 3)

            header_item = create_item("Итог за день")
            table.setItem(start, 0, header_item)

            dialog.combo_day = _create_comboBox(dialog, start, table)

            create_data_header_section_and_insert(start+2)
            create_data_and_insert(start+3)

        def create_month_data(start):
            table.setSpan(start, 0, 1, 3)
            header_item = create_item("Итог за Месяц")
            table.setItem(start, 0, header_item)


            table.setSpan(start+1, 0, 1, 3)
            dialog.combo_month = _create_comboBox(dialog, start, table)

            create_data_header_section_and_insert(start+2)
            create_data_and_insert(start+3)

        create_day_data(0)
        create_month_data(13)

        table.setColumnWidth(0, 260)  # Устанавливаем ширину первой колонки 150 пикселей
        table.setColumnWidth(1, 130)  # Вторая колонка — 100 пикселей
        table.setColumnWidth(2, 130)  # Третья колонка — 200 пикселей

        # Можно скрыть заголовки, если нужно
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)

        # table.raise_()
        return table
    except Exception as a:
        print(a, "create_right_panel_info")
    finally:
        return table

def create_search_tab(dialog):
    # Создаем контейнер для горизонтального layout
    dialog.search_widget = QWidget(dialog)  # Это контейнер для элементов
    dialog.search_layout = QHBoxLayout(dialog.search_widget)

    # Поле ввода(поиск)
    dialog.search_input = QLineEdit(dialog)
    dialog.search_input.setPlaceholderText("Введите название товара...")
    dialog.search_input.setFixedSize(570, 53)  # Увеличенные размеры


    # Кнопка 1 (Поиск)
    dialog.search_button = QPushButton("🔍 Поиск", dialog)
    dialog.search_button.setFixedSize(120, 53)  # Увеличенные размеры
    # dialog.search_button.setStyleSheet(dialog.search_handler.set_style_btn(False))


    # Кнопка 2 (Очистить)
    dialog.clear_button = QPushButton("✖ Сброс", dialog)
    dialog.clear_button.setFixedSize(120, 53)  # Увеличенные размеры
    # dialog.clear_button.setStyleSheet(dialog.search_handler.set_style_btn(True))

    # Добавляем все элементы в горизонтальный layout
    dialog.search_layout.addWidget(dialog.search_input)
    dialog.search_layout.addWidget(dialog.search_button)
    dialog.search_layout.addWidget(dialog.clear_button)

    # 🔹 Настроим контейнер с layout
    dialog.search_widget.setFixedSize(880, 63)  # Фиксированный размер контейнера
    dialog.search_layout.setContentsMargins(5, 0, 5, 0)  # Отступы внутри контейнера
    dialog.search_layout.setSpacing(5)  # Расстояние между кнопками

    # Перемещаем контейнер (search_widget) с layout
    dialog.search_widget.move(550, 7)  # Перемещаем контейнер в нужное место

    dialog.search_button.setAutoDefault(False)
    dialog.clear_button.setAutoDefault(False)