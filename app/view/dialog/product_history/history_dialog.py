from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget,
)
from PyQt5.QtCore import Qt, QTimer

from view.dialog.product_history.tabs.history_tab.calculator.enums import ActionType
from .tabs.list_products_tab import ProductsTabLoader
from .tabs.sum_list_products_tab import SumProductsTabLoader
from .tabs.history_tab.logic import HistoryLoader, TableStatiscticUIManager

from .tabs.history_tab import (
    create_history_tab, create_details_widget,
    create_date_first_line, create_right_panel_info, create_search_tab, create_tree_item,
    create_custom_cell_widget, get_data_dict_in_tree_item
)
from view.dialog.product_history.utils import decimal_to_str_trimmed_for_amount, decimal_to_str_trimmed_for_quantity
from search_global import create_search_result_list

from view.dialog.product_history.handlers import SearchHandler
from utils.decorators import debug_decorator
from PyQt5.QtCore import QEvent


class DataDialog(QDialog):
    def __init__(self, db):
        super().__init__()

        self.setWindowTitle("История операций")
        self.setGeometry(0, 0, 1920, 1080)

        # Инициализация переменных
        self.open_details_row = None  # Словарь для отслеживания открытых деталей
        self.db = db  # База данных
        self.open_item = None

        self.create_tabs() # Создаем вкладки
        self.create_other_widgets() # Остальные виджеты

        self.set_events()

        # self.grabMouse()
        self.first_loads_data_tabs()

    def set_events(self):
        # Подключаем обработчик скролла
        self.installEventFilter(self)
        self.tabs.currentChanged.connect(self.on_tab_change)

        self.tab_changes.verticalScrollBar().valueChanged.connect(self.on_scroll)
        self.tab_changes.itemClicked.connect(self.on_row_click)  # Сигнал для обработки клика
        self.tab_changes.verticalScrollBar().valueChanged.connect(self.on_scroll)

        # Привязка сигналов
        self.combo_day.currentIndexChanged.connect(self.table_statistic_manager.on_combo_day_change)
        self.combo_month.currentIndexChanged.connect(self.table_statistic_manager.on_combo_month_change)

        self.scroll_debounce_timer = QTimer()
        self.scroll_debounce_timer.setSingleShot(True)
        self.scroll_debounce_timer.timeout.connect(lambda: self.history_loader.load_changes(next_chunk=True))

        self.list_search.itemClicked.connect(self.search_handler.select_product_from_search_list)
        self.search_input.textChanged.connect(self.search_handler.on_search_text_changed)
        self.search_input.returnPressed.connect(self.search_handler.entered_enter_key_input)
        self.search_button.clicked.connect(self.search_handler.entered_enter_key_input)
        self.clear_button.clicked.connect(self.search_handler.entered_false_search_input_key)

    @debug_decorator
    def create_other_widgets(self):
        create_date_first_line(self)
        create_search_tab(self)  # Создаем tab поиска
        self.right_panel = create_right_panel_info(self)
        self.history_loader = HistoryLoader(dialog=self)
        self.table_statistic_manager = TableStatiscticUIManager(self)

        self.list_search = create_search_result_list(self, self.search_input)

        self.search_handler = SearchHandler(self)

        create_details_widget(self)  # Создаем отдельный виджет для отображения подробностей



    def create_tabs(self):
        self.tabs = QTabWidget()

        # Получаем доступ к QTabBar, который управляет вкладками
        tab_bar = self.tabs.tabBar()
        self.tabs.tabBar().setObjectName("my_tab_bar")  # Устанавливаем имя

        # Устанавливаем высоту вкладок
        self.tabs.setStyleSheet("""
                    QTabBar::tab {
                        height: 50px; /* Высота по умолчанию для всех вкладок */
                        font-size: 18px;
                        width: 175px;
                        border: 1px solid #646464;   
                    }
                    QTabBar::tab:selected {
                        background-color: #73B5E7;
                    }
                """)

        create_history_tab(self)                    # Вкладка 1 - Изменения товаров
        self.products_tab = ProductsTabLoader(self) # Вкладка 2 - Список товаров
        self.sum_tab = SumProductsTabLoader(self)   # Вкладка 3 - Сумма товаров и количества

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def first_loads_data_tabs(self):
        self.history_loader.load_changes()  # 🔹 Загружаем данные вкладка 1
        self.products_tab.load_products()   # 🔹 Загружаем данные вкаладка 2
        self.sum_tab.load_data()            # 🔹 Загружаем данные вкаладка 3

    # --------------------------------------------------------------------------
    def update_table(self):
        """Перерисовывает таблицу"""
        self.tab_changes.viewport().update()  # Обновляем область просмотра таблицы

    @staticmethod
    def formatting_list_products_sale(list_value: list | tuple) -> list:
        new_list = []
        for i in list_value:
            pass


    def set_open_item(self, item):
        if not self.open_item is None:
            if self.open_item != item:
                self.open_item.setExpanded(False)
                self.open_item = item
                self.open_item.setExpanded(True)
            else:
                item.setExpanded(False)
                self.open_item = None
        else:
            self.open_item = item
            self.open_item.setExpanded(True)

    @debug_decorator
    def on_scroll(self, value):
        """Обработка события скролла"""
        # self.hide_details()
        self.history_loader.update_ui_from_top_row()
        bar = self.tab_changes.verticalScrollBar()
        if bar.maximum() - value <= 2:
            # Перезапускаем таймер: сработает через 200 мс, если скролл не повторится
            self.scroll_debounce_timer.start(200)  # 200 мс
    # --------------------------------------------------------

    # Event Handlers
    @debug_decorator
    def on_tab_change(self, index):
        """Вызывается при смене вкладки.index - индекс новой активной вкладки."""
        # self.search_input.setText("")
        # self.search_handler.entered_false_search_input_key(False)
        # self.date_label_first_line.setText("")

        if index == 0:
            self.history_loader.update_ui_from_top_row()
            self.search_widget.show()
        elif index == 1:
            self.search_widget.show()
            self.date_widget_first_line.hide()
            self.products_tab.load_products()
        elif index == 2:
            self.date_widget_first_line.hide()
            self.search_widget.hide()

    def get_f(self, row):
        name, quantity, sale_or_info = row[3:]
        formatted_quantity = decimal_to_str_trimmed_for_quantity(quantity)
        formatted_sale_or_info = decimal_to_str_trimmed_for_amount(sale_or_info)
        return name, formatted_quantity, formatted_sale_or_info

    def get_formatting_data_in_sale(self, raw_query):
        new_list = []
        for row in raw_query:
            new_row = self.get_f(row)
            new_list.append(new_row)

        return new_list

    def set_v(self, item):
        is_union = ActionType.get_value(item.text(0)) == ActionType.UNION

        data_dict = get_data_dict_in_tree_item(item)
        is_sale = data_dict.get("sale_id")
        id_row = data_dict.get("sale_id") if is_sale else data_dict.get("change_id")

        items = self.db.get_action_details(id_row, is_sale)
        items = self.get_formatting_data_in_sale(items)


        child_item = create_tree_item()
        widget = create_custom_cell_widget(items, is_union)
        item.addChild(child_item)
        child_item.setFirstColumnSpanned(True)
        self.tab_changes.setItemWidget(child_item, 0, widget)
        self.set_open_item(item)

    @debug_decorator
    def on_row_click(self, item, col):
        """Обработчик кликов по строке"""
        self.get_child_and_view(item)

    def get_child_and_view(self, item):
        if item.parent() is not None:
            return

        self.search_input.setText("")

        # Если есть дети, но это заглушка — удаляем её и грузим заново
        if item.childCount() > 0:
            first_child = item.child(0)

            if first_child.text(0) == "" or first_child.text(0) == "Загрузка...":
                item.takeChildren()  # Удаляем заглушку и загружаем данные
                self.set_v(item)
            else:
                return  # Если реальные дети — выходим


    @debug_decorator
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            key = event.key()
            text = event.text()

            # Стрелки вверх/вниз
            if key in (Qt.Key_Up, Qt.Key_Down):
                if not self.list_search.hasFocus():
                    self.list_search.setCurrentRow(0)
                    self.list_search.setFocus()
                return True  # событие обработано

            # Enter
            elif key == Qt.Key_Return:
                if self.list_search.hasFocus():
                    self.search_handler.select_product_from_search_list(None)
                    return True

            # Escape
            elif key == Qt.Key_Escape:
                return False  # можно пропустить дальше

            # Буквы и цифры
            elif text.isalpha() or text.isdigit():
                if not self.search_input.hasFocus():
                    self.search_input.setFocus()
                cursor_pos = self.search_input.cursorPosition()
                current_text = self.search_input.text()
                new_text = current_text[:cursor_pos] + text + current_text[cursor_pos:]
                self.search_input.setText(new_text)
                self.search_input.setCursorPosition(cursor_pos + 1)
                return True  # событие обработано

        return False  # все остальные события передаем дальше

