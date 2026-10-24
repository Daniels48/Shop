from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from view.dialog.product_history.utils import decimal_to_str_trimmed_for_amount, decimal_to_str_trimmed_for_quantity


class SumProductsTabLoader:
    def __init__(self, dialog):
        self.dialog = dialog
        self.table = QTableWidget()

        self.dialog.tabs.addTab(self.table, "Сумма товаров")
        self.setup_table()
        self.load_data()

    def setup_table(self):
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(
            ["Колличество товаров", "Сумма товаров", "Стоимость всех товаров"]
        )

        self.table.setStyleSheet("""
            QHeaderView::section {
                font-weight: bold;
                font-size: 11pt;
            }
        """)

        font = QFont()
        font.setPointSize(14)
        self.table.setFont(font)

        self.table.setColumnWidth(0, 300)
        self.table.setColumnWidth(1, 300)
        self.table.setColumnWidth(2, 300)


    def create_cell_item(self, text):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        return item

    def insert_item(self, item, idx):
        self.table.setItem(0, idx, item)


    def init_table(self):
        self.table.setRowCount(0)
        self.table.insertRow(0)


    def load_data(self):
        items_raw, quantity_raw, amount_raw = self.dialog.db.get_inventory_summary()
        self.init_table()

        total_items = str(items_raw) + " шт."
        total_quantity = decimal_to_str_trimmed_for_quantity(quantity_raw) + " шт. (кг.)"
        total_amount = decimal_to_str_trimmed_for_amount(amount_raw)

        list_value = [total_items, total_quantity, total_amount]

        for idx, value in enumerate(list_value):
            item = self.create_cell_item(value)
            self.insert_item(item, idx)
