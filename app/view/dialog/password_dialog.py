from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox

password = "20002000"

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Введите пароль")
        self.setFixedSize(500, 150)

        layout = QVBoxLayout()

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setStyleSheet("height:40px;font-size:30px;border-radius:10px;border:1px solid black; padding-left:5px;")
        self.password_input.setEchoMode(QLineEdit.Password)  # Скрывает вводимые символы
        layout.addStretch(1)
        layout.addWidget(self.password_input)
        layout.addStretch(1)
        self.confirm_button = QPushButton("Подтвердить")
        self.confirm_button.setStyleSheet("height:40px;background-color:#01B4E4;font-size:18px;color:white;font-size:30px;border-radius:15px;")
        self.confirm_button.clicked.connect(self.check_password)
        layout.addWidget(self.confirm_button)

        self.setLayout(layout)

    def check_password(self):
        if self.password_input.text() == password:  # Здесь задаем правильный пароль
            self.accept()  # Закрываем диалог с успешным результатом
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный пароль!")
            self.password_input.setText("")


