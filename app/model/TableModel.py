from app.model.ProductModel import Product
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QItemSelectionModel
from decimal import Decimal

class ProductTableModel(QAbstractTableModel):
    def __init__(self, table_view=None, main_window=None, parent=None):
        super().__init__(parent)
        self._headers = ["№", "Наименование", "Цена", "Кол-во", "Cумма"]
        self._products = []  # Храним список экземпляров класса Product
        self.product_index = {}
        self.table_view = table_view
        self.main_window = main_window

    def rowCount(self, parent=QModelIndex()):
        return len(self._products)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        try:
            if not index.isValid():
                return None
            if role == Qt.DisplayRole:
                row = index.row()
                col = index.column()
                product = self._products[row]
                if col == 0:
                    return str(row + 1)
                elif col == 1:
                    return str(product.name)
                elif col == 2:
                    return self.trim_trailing_zeros(product.price)
                elif col == 3:
                    return self.trim_trailing_zeros(product.current_quantity)
                elif col == 4:
                    return self.trim_trailing_zeros(product.total)
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
            return None
        except Exception as a:
            print(a)

    def trim_trailing_zeros(self, value):
        """Удаляет лишние нули справа и точку, если после нее ничего не остается"""
        if isinstance(value, float) or isinstance(value, int) or isinstance(value, Decimal):
            value = str(value)
        return value.rstrip('0').rstrip('.') if '.' in value else value

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal and 0 <= section < len(self._headers):
            return self._headers[section]
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def add_product(self, barcode, name, price, quantity, id):
        """Добавляет товар в таблицу и обновляет количество, если товар уже есть."""
        if id in self.product_index:
            # Товар уже есть, просто обновляем количество
            product = self.product_index[id]
            row = self._products.index(product)  # Получаем индекс строки товара
            product.update_quantity(1)

            # Оповещаем таблицу, что данные в строке изменились
            self.dataChanged.emit(self.index(row, 3), self.index(row, 4))
            # Выделяем товар в таблице
            self.select_row(row)
        else:
            # Новый товар — добавляем его в список
            product = Product(barcode, name, quantity, price, id, self.main_window)
            if not product.error:
                row = len(self._products)  # Новый индекс строки
                self.beginInsertRows(QModelIndex(), row, row)
                self._products.append(product)
                self.product_index[id] = product
                self.endInsertRows()
                # Выделяем товар в таблице
                self.select_row(row)



    def select_row(self, row):
        """Выделяет указанную строку в таблице."""
        if 0 <= row < len(self._products):
            index = self.index(row, 0)  # Получаем индекс первой колонки нужной строки
            if self.table_view and self.table_view.selectionModel():
                selection_model = self.table_view.selectionModel()
                selection_model.clearSelection()
                selection_model.select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
                self.table_view.scrollTo(index)
                self.table_view.setCurrentIndex(index)

    def remove_product_by_row(self, row):
        """Удаляет товар по номеру строки."""
        if 0 <= row < len(self._products):
            product = self._products[row]
            del self.product_index[product.id]  # Удаляем товар из индекса
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._products[row]  # Удаляем объект из списка товаров
            self.endRemoveRows()

    def get_selected_row(self):
        """Возвращает номер выделенной строки в таблице, или None, если ничего не выделено."""
        try:
            selected_indexes = self.table_view.selectionModel().selectedRows()
            if len(selected_indexes) == 1:  # Проверка, что выбрана только одна строка
                return selected_indexes[0].row()
        except Exception as a:
            print(a)


        return None  # Если ни одна строка не выбрана или выбрано больше одной

    def get_product_by_row(self, row):
        """Возвращает объект Product по номеру строки."""
        if 0 <= row < len(self._products):
            return self._products[row]
        return None

    def clear(self):
        self.beginResetModel()
        self._products = []
        self.product_index = {}
        self.endResetModel()

    def get_total(self):
        """Возвращает общую сумму всех товаров в таблице."""
        return sum(product.total for product in self._products)

    def get_product_list(self):
        return self._products



def get_stylesheet(fz_tbl, fz_sec, border_color):
    return f"""
           QTableView {{
               background-color: white;
               color: black;
               gridline-color: black;
               font-size: {fz_tbl}px;
           }}

           QHeaderView::section {{
               background-color: #38495C;
               color: white;
               padding: 10px;
               font-weight: 600;
               font-size: {fz_sec}px;
               border: 1px solid {border_color};
           }}

           QTableView::item {{
               border: 1px solid {border_color};
               padding-left: 5px;
               padding-right: 5px;
               font-size: {fz_tbl}px;  /* Задаем шрифт для обычных ячеек */
           }}

           QTableView::item:selected {{
               background-color: #04A8FB;;
               color: black;
               font-weight: 700;  /* Делаем текст жирным при выделении */
               font-size: {fz_tbl}px;  /* Фиксируем размер шрифта при выделении */
           }}

           QTableView::item:last-child {{
               border-right: none;
           }}
           """
