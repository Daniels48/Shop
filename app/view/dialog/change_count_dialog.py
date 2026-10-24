from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator


class CountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Введите количество")
        self.setFixedSize(500, 200)

        layout = QVBoxLayout()

        # Поле ввода (только float, максимум 2 знака после запятой)
        self.input_field = QLineEdit(self)
        validator = QDoubleValidator(0, 999999, 3)  # Мин. и макс. число, 2 знака после запятой
        validator.setNotation(QDoubleValidator.StandardNotation)  # Обычная запись (не экспоненциальная)
        self.input_field.setValidator(validator)
        self.input_field.setStyleSheet(
            "height:40px; font-size:30px; border-radius:10px; padding-left:5px; border:1px solid black;")
        self.input_field.setPlaceholderText("Введите новое количество ...")

        layout.addStretch(1)
        layout.addWidget(self.input_field)
        layout.addStretch(1)

        # Кнопки
        button_layout = QHBoxLayout()

        # Кнопка запятой
        self.comma_button = QPushButton("Запятая [,]")
        self.comma_button.setStyleSheet(
            "height:50px; font-size:30px; border-radius:10px; background-color:#D3D3D3;")
        self.comma_button.clicked.connect(self.insert_comma)
        button_layout.addWidget(self.comma_button)

        # Кнопка подтверждения
        self.confirm_button = QPushButton("Подтвердить")
        self.confirm_button.setStyleSheet(
            "height:50px; font-size:30px; color:white; border-radius:10px; background-color:#01B4E4;")
        self.confirm_button.clicked.connect(self.close_dialog)
        button_layout.addWidget(self.confirm_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def insert_comma(self):
        """Добавляет запятую в поле ввода"""
        current_text = self.input_field.text()
        if "," not in current_text:
            self.input_field.setText(current_text + ",")
        self.input_field.setFocus()

    def close_dialog(self):
        if self.get_value():
            if not float(self.get_value()) > 0:
                QMessageBox.warning(self, "Ошибка", "Значение должно быть больше нуля", QMessageBox.Ok)
            else:
                self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Поле не должно быть пустым", QMessageBox.Ok)

    def keyPressEvent(self, event):
        """Обработка нажатия клавиши"""
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.close_dialog()
        if event.key() == Qt.Key_Escape:
            self.close()  # Закрытие окна при нажатии Esc

    def get_value(self):
        return self.input_field.text().replace(",", ".")