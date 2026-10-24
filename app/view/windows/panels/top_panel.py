from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt, QDateTime


class TopPanel(QWidget):
    def __init__(self, number_check: int, parent=None):
        super().__init__(parent)

        self.init_ui(number_check)
        self.init_timer()

    def init_ui(self, number_check: int):
        self.setStyleSheet("background-color: #0087CD;")
        self.setFixedHeight(45)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)

        # Номер чека
        self.check_label = QLabel(f"Чек № {number_check}",self)
        self.check_label.setStyleSheet("color: white; font-size: 20px;")
        layout.addWidget(self.check_label)

        # Текущее время
        self.time_label = QLabel(self)
        self.time_label.setAlignment(Qt.AlignRight)
        self.time_label.setStyleSheet("color: white; font-size: 20px;")
        layout.addWidget(self.time_label)

    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.update_time()

    def update_time(self):
        format_date = "d MMMM yyyy г. hh:mm:ss"
        current_datetime = QDateTime.currentDateTime().toString(format_date).lower()
        self.time_label.setText(current_datetime)

    def set_check_number(self, number_check: int):
        self.check_label.setText(f"Чек № {number_check}")
