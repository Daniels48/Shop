from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from app.view.dialog.product_history.utils import decimal_to_str_trimmed_for_amount, decimal_to_str_trimmed_for_quantity


class ProductsTabLoader:
    def __init__(self, dialog):
        self.dialog = dialog
        self.table = QTableWidget()
        self.last_sorted_column = None
        self.ascending = True

        self.dialog.tabs.addTab(self.table, "Список товаров")
        self.setup_table()

    def setup_table(self):
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Штрихкод", "Цена", "Кол-во"])

        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 750)
        self.table.setColumnWidth(2, 250)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 100)

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(False)
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_click)

        self.load_products()

    def on_header_click(self, index):
        if self.last_sorted_column == index:
            self.ascending = not self.ascending
        else:
            self.last_sorted_column = index
            self.ascending = True

        sort_fields = {0: "id", 1: "name", 2: "barcode", 3: "price_sale", 4: "quantity"}
        sort_by = sort_fields.get(index, "id")
        self.load_products(sort_by, self.ascending)

    def load_products(self, sort_by="id", ascending=True, barcode=None):
        products = self.dialog.db.get_all_products(sort_by, ascending, barcode)

        self.table.setRowCount(len(products))

        for row_idx, row_data in enumerate(products):
            for col_idx, col_data in enumerate(row_data):
                dct_value = {3:decimal_to_str_trimmed_for_amount(col_data),
                             4:decimal_to_str_trimmed_for_quantity(col_data)}

                text = dct_value.get(col_idx, str(col_data))
                item = QTableWidgetItem(text)
                if col_idx in (0, 3, 4,):
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)




