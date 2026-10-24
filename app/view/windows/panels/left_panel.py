from PyQt5.QtWidgets import QWidget, QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QTableView,QHeaderView,QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from utils.get_path import get_resourse_path_icon
from model.TableModel import ProductTableModel, get_stylesheet


class LeftPanel(QWidget):
    def __init__(self, presenter, parent=None):
        super().__init__(parent)

        self.presenter = presenter
        self.main_window = parent

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.add_product_name_input(layout)
        self.add_table_product(layout)
        self.add_buttons_sale(layout)

    # Название товара и иконка сканера
    def add_product_name_input(self, layout, font_size=32):
        input_container = QWidget(self)
        input_container.setObjectName("InputContainer")

        input_layout = QHBoxLayout(input_container)
        input_layout.setAlignment(Qt.AlignVCenter)
        input_layout.setContentsMargins(10, 0, 10, 0)
        input_layout.setSpacing(15)

        self.icon_label = QLabel(self)
        barcode_path = get_resourse_path_icon("barcoder.ico")
        self.icon_label.setPixmap(QPixmap(barcode_path).scaled(50, 50, Qt.KeepAspectRatio))
        self.icon_label.setFixedSize(50, 50)

        self.product_name_label = QLabel(self.presenter.name_, input_container)
        self.product_name_label.setStyleSheet(f"font-size: {font_size}px; border: none;")
        self.product_name_label.setFixedHeight(40)
        self.product_name_label.setAlignment(Qt.AlignVCenter)

        input_layout.addWidget(self.icon_label)
        input_layout.addWidget(self.product_name_label)

        input_container.setStyleSheet(
            "QWidget#InputContainer {"
            "background-color: white;"
            "border-radius: 10px;"
            "padding: 5px;"
            "border: 1px solid black;"
            "}"
        )
        input_container.setFixedHeight(60)

        layout.addWidget(input_container)
        layout.addSpacing(20)

    # Таблица товаров
    def add_table_product(self, layout, fz_tbl=35, fz_sec=36,
                          border_color="black"):
        self.table_view = QTableView(self)
        self.product_model = ProductTableModel(
            self.table_view,
            self.main_window,
        )
        self.table_view.setModel(self.product_model)

        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.verticalHeader().setVisible(False)

        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self.table_view.setColumnWidth(0, self.presenter.width_number)
        self.table_view.setColumnWidth(2, self.presenter.width_price)
        self.table_view.setColumnWidth(3, self.presenter.width_count)
        self.table_view.setColumnWidth(4, self.presenter.width_sum)

        self.table_view.setStyleSheet(get_stylesheet(fz_tbl, fz_sec, border_color))
        self.table_view.verticalHeader().setDefaultSectionSize(50)

        layout.addWidget(self.table_view)

        # Пока оставляем текущие обработчики,
        # чтобы не сломать существующее поведение.
        self.table_view.installEventFilter(self.main_window)
        self.table_view.keyPressEvent = self.main_window.handle_key_press

        self.table_view.selectionModel().selectionChanged.connect(self.presenter.update_buttons_state)

    # Кнопки отмены, оплаты и итоговая сумма
    def add_buttons_sale(self, layout):
        button_layout = QHBoxLayout()

        self.cancel_button = QPushButton("Отмена  [Esc]", self)
        self.pay_button = QPushButton("Оплатить  [P]", self)

        self.set_button_style(self.cancel_button, "#ff4d4d")
        self.set_button_style(self.pay_button, "#4CAF50")

        self.total_label = QLabel("Итог: 0 ₽", self)
        self.total_label.setAlignment(Qt.AlignBottom)
        self.total_label.setStyleSheet(
            "background-color: #f0f0f0;"
            "padding: 10px;"
            "border-radius: 5px;"
            "font-weight: bold;"
            "height: 50px;"
            "font-size: 60px;"
        )

        total_layout = QHBoxLayout()
        total_layout.addWidget(self.total_label)

        button_layout.addWidget(self.cancel_button, 1)
        button_layout.addWidget(self.pay_button, 1)
        button_layout.addLayout(total_layout, 1)
        button_layout.setAlignment(Qt.AlignBottom)

        layout.addLayout(button_layout)

        self.cancel_button.clicked.connect(self.presenter.clear_table)
        self.pay_button.clicked.connect(lambda checked=False: self.presenter.open_payment_dialog())

    @staticmethod
    def set_button_style(button, background_color, font_size=40):
        button.setStyleSheet(
            f"background-color: {background_color};"
            "color: white;"
            "padding: 10px;"
            "border-radius: 20px;"
            "height: 50px;"
            f"font-size: {font_size}px;"
            "font-weight: 700;"
        )
        button.setEnabled(False)

    # Методы для обновления интерфейса извне
    def set_product_name(self, name: str):
        self.product_name_label.setText(name)

    def set_total(self, total: str):
        self.total_label.setText(f"Итог: {total} ₽")

    def set_buttons_enabled(self, cancel: bool, pay: bool):
        self.cancel_button.setEnabled(cancel)
        self.pay_button.setEnabled(pay)