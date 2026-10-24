# import os
# import hashlib
# from datetime import datetime, timedelta
#
# from PyQt5.QtWidgets import (
#     QDialog, QVBoxLayout, QHBoxLayout,
#     QLabel, QLineEdit, QTextEdit, QPushButton
# )
# from PyQt5.QtGui import QIntValidator
# from PyQt5.QtCore import pyqtSignal, Qt
#
#
# from api_1C.server_http import PyQtHttpServer
#
#
# class ServerDialog(QDialog):
#     _instance = None  # Статическая переменная для хранения единственного экземпляра
#     dialog_closed = pyqtSignal()  # Новый сигнал для закрытия диалога
#
#     def __init__(self, main_windows, presenter):
#         # Если экземпляр уже существует, возвращаем его
#         if ServerDialog._instance is not None:
#             self.__dict__ = ServerDialog._instance.__dict__
#             return
#
#         super().__init__()
#         ServerDialog._instance = self  # Сохраняем экземпляр
#
#         self.main_windows = main_windows
#         self.presenter = presenter
#         self.server = PyQtHttpServer()
#         self.server.log_message.connect(self.add_log)
#         self.server.request_received.connect(self.action_server)
#
#         self.setWindowTitle("Управление сервером")
#         self.resize(1550, 800)
#
#         self.main_layout = QVBoxLayout()
#         self.top_layout = QHBoxLayout()
#         self.btn_layout = QHBoxLayout()
#         self.main_layout.addLayout(self.top_layout)
#
#         # --- Лог сервера ---
#         self.log = QTextEdit()
#
#         style_log = "border-radius:25px; padding: 12px; color: black; font-size: 20px; " \
#                     "background-color: white; border: 1px solid black;"
#
#         self.log.setStyleSheet(style_log)
#         self.log.setReadOnly(True)
#         self.main_layout.addWidget(self.log)
#         self.main_layout.addLayout(self.btn_layout)
#
#         self.host_layout = self.create_host()
#         self.port_layout = self.create_port()
#         self.target_ip_layout = self.create_target_ip()
#         self.target_port_layout = self.create_target_port()
#
#         # --- Кнопки Старт / Стоп ---
#         self.start_btn = QPushButton("Старт")
#         self.stop_btn = QPushButton("Стоп")
#         self.start_btn.setStyleSheet(self.style_btn(True, False))
#         self.stop_btn.setStyleSheet(self.style_btn(False, False))
#
#         self.btn_layout.addWidget(self.start_btn)
#         self.btn_layout.addWidget(self.stop_btn)
#
#         self.setLayout(self.main_layout)
#
#         # --- Сигналы кнопок ---
#         self.start_btn.clicked.connect(self.start_server)
#         self.stop_btn.clicked.connect(self.stop_server)
#         self.change_inputs(False)
#         self.initialize_logging()
#
#     def keyPressEvent(self, event):
#         """Обработка нажатия клавиш"""
#         if event.key() == Qt.Key_Escape:
#             # При нажатии Esc вызываем тот же метод, что и при закрытии крестиком
#             self.close()
#         else:
#             super().keyPressEvent(event)
#
#     def closeEvent(self, event):
#         """Переопределяем закрытие окна"""
#         # Испускаем сигнал перед закрытием
#         self.dialog_closed.emit()
#         self.hide()  # Скрываем окно вместо уничтожения
#
#         if hasattr(self, 'main_windows') and self.main_windows:
#             self.main_windows.table_view.setFocus()
#
#         event.ignore()  # Предотвращаем стандартное закрытие
#
#     def showEvent(self, event):
#         """При показе окна обновляем состояние кнопок"""
#         super().showEvent(event)
#         # Обновляем состояние интерфейса в зависимости от состояния сервера
#         if self.server.is_running:
#             self.change_inputs(True)
#             self.start_btn.setStyleSheet(self.style_btn(True, True))
#             self.start_btn.setEnabled(False)
#         else:
#             self.change_inputs(False)
#             self.start_btn.setStyleSheet(self.style_btn(True, False))
#             self.start_btn.setEnabled(True)
#
#     @classmethod
#     def get_instance(cls, main_windows=None, presenter=None):
#         """Статический метод для получения экземпляра диалога"""
#         if cls._instance is None:
#             cls._instance = cls(main_windows, presenter)
#         return cls._instance
#
#
#     def ean13_generator(self, product_name):
#         """Простой генератор EAN-13 подобных кодов"""
#
#         # Нормализуем название
#         normalized_name = product_name.lower().strip().replace(' ', '_')
#
#         # Хеш
#         hash_obj = hashlib.md5(normalized_name.encode('utf-8'))
#         hash_hex = hash_obj.hexdigest()
#
#         # Конвертируем hex в цифры (a=0, b=1, ..., f=5)
#         digit_map = {'a': '0', 'b': '1', 'c': '2', 'd': '3', 'e': '4', 'f': '5'}
#         digits = ''
#         for char in hash_hex:
#             if char in digit_map:
#                 digits += digit_map[char]
#             elif char.isdigit():
#                 digits += char
#
#         # Берем 12 цифр
#         base_code = digits[:12].ljust(12, '0')
#
#         # Контрольная сумма EAN-13
#         total = 0
#         for i, digit in enumerate(base_code):
#             if i % 2 == 0:
#                 total += int(digit) * 1
#             else:
#                 total += int(digit) * 3
#         checksum = (10 - (total % 10)) % 10
#
#         return base_code + str(checksum)
#
#
#     def action_server(self, url, data):
#         if url == "/add_product":
#             self.add_product(data)
#
#
#     def add_product(self, data):
#         name = data.get("name")
#         quantity = data.get("quantity")
#         price = data.get("price")
#         barcode = self.ean13_generator(name)
#
#         try:
#             id_product = self.presenter.db.get_product_id_by_name(name)
#
#             if id_product:
#                 add_quantity = self.presenter.db.set_update_quantity_product(id_product, quantity)
#                 rest = self.presenter.db.update_price_product(id_product, float(price))
#
#             else:
#                 result_db = self.presenter.db.add_new_product([barcode], name, price, quantity)
#                 rest = self.presenter.db.update_price_product(id_product, float(price))
#
#             res = self.presenter.process_barcode(barcode, True, quantity=quantity)
#
#             # self.main_windows.main_window.table_view.setFocus()
#         except Exception as a:
#             print(a)
#
#     # Остальные методы остаются без изменений...
#     def create_target_ip(self):
#         layout_host = QVBoxLayout()
#         self.text_ip_target = QLabel("Ip получателя")
#         self.text_ip_target.setStyleSheet(self.style_text())
#
#         self.input_ip_target = QLineEdit(self)
#         self.input_ip_target.setPlaceholderText("localhost")
#
#         layout_host.addWidget(self.text_ip_target)
#         layout_host.addWidget(self.input_ip_target)
#
#         self.top_layout.addLayout(layout_host)
#
#         return layout_host
#
#     def create_target_port(self):
#         layout_port = QVBoxLayout()
#
#         self.text_port_target = QLabel("Порт получателя")
#         self.text_port_target.setStyleSheet(self.style_text())
#
#         self.input_port_target = QLineEdit(self)
#         validator = QIntValidator(0, 9999)
#         self.input_port_target.setPlaceholderText("8081")
#         self.input_port_target.setValidator(validator)
#
#         layout_port.addWidget(self.text_port_target)
#         layout_port.addWidget(self.input_port_target)
#
#         self.top_layout.addLayout(layout_port)
#         return layout_port
#
#     def create_port(self):
#         layout_port = QVBoxLayout()
#
#         self.text_port = QLabel("Порт")
#         self.text_port.setStyleSheet(self.style_text())
#
#         self.input_port = QLineEdit(self)
#         self.input_port.setPlaceholderText("8081")
#         validator = QIntValidator(0, 9999)
#         self.input_port.setValidator(validator)
#
#         layout_port.addWidget(self.text_port)
#         layout_port.addWidget(self.input_port)
#
#         self.top_layout.addLayout(layout_port)
#         return layout_port
#
#     def create_host(self):
#         layout_host = QVBoxLayout()
#
#         self.text_host = QLabel("Хост")
#         self.text_host.setStyleSheet(self.style_text())
#
#         self.input_host = QLineEdit(self)
#         self.input_host.setPlaceholderText("localhost")
#
#         layout_host.addWidget(self.text_host)
#         layout_host.addWidget(self.input_host)
#
#         self.top_layout.addLayout(layout_host)
#
#         return layout_host
#
#     def change_inputs(self, off=False):
#         self.input_host.setStyleSheet(self.style_inputs(off))
#         self.input_port.setStyleSheet(self.style_inputs(off))
#         self.input_port_target.setStyleSheet(self.style_inputs(off))
#         self.input_ip_target.setStyleSheet(self.style_inputs(off))
#
#         self.input_host.setEnabled(not off)
#         self.input_port.setEnabled(not off)
#         self.input_port_target.setEnabled(not off)
#         self.input_ip_target.setEnabled(not off)
#
#     def style_btn(self, is_enter, is_false):
#         color = f"rgba(255, 0, 0, {200 if not is_false else 60})" if not is_enter else f"rgba(0, 255, 0, {200 if not is_false else 60})"
#         return f"color:#F0F0F0;background-color:{color};border-radius:15px;height:50px;font-size:29px;font-weight:700;"
#
#     def style_inputs(self, off=False):
#         bcgrnd = "background-color: rgba(0, 0, 0, 100);" if off else "white"
#         return f"height:30px; font-size:20px;border-radius:5px;border:1px solid black; padding-left: 3px;{bcgrnd}"
#
#     def style_text(self):
#         return "font-size:24px;"
#
#     def start_server(self):
#         self.change_inputs(True)
#
#         self.start_btn.setStyleSheet(self.style_btn(True, True))
#         self.start_btn.setEnabled(False)
#
#         host = self.input_host.text()
#         port = self.input_port.text()
#         target_ip = self.input_ip_target.text()
#         target_port = self.input_port_target.text()
#
#         if host: self.server.host = host
#         if port: self.server.port = int(port)
#         if target_ip: self.server.ip_target = target_ip
#         if target_port: self.server.port_target = int(target_port)
#
#         # Перезапуск, если уже запущен
#         if self.server.is_running:
#             self.server.stop_server()
#
#         self.server.start()
#
#     def stop_server(self):
#         try:
#             self.server.stop_server()
#             self.change_inputs(False)
#             self.start_btn.setStyleSheet(self.style_btn(True, False))
#             self.start_btn.setEnabled(True)
#         except Exception as a:
#             print(a)
#
#     def time_operation(self):
#         return  datetime.now().strftime("%d.%m.%y %H:%M:%S")
#
#     def get_today(self):
#         return datetime.now().strftime("%d.%m.%y")
#
#     def get_log_dir(self):
#         return "logs"
#
#     def add_log(self, text):
#         timestamp = self.time_operation()
#         log_entry = f"{timestamp} [INFO] {text}"
#
#         # Добавляем в QTextEdit
#         self.log.append(log_entry)
#
#         # Записываем в файл
#         self._write_log_to_file(log_entry)
#
#         # Проверяем и очищаем старые записи (раз в день)
#         self._clean_old_logs()
#
#     def _write_log_to_file(self, log_entry):
#         """Запись лога в файл"""
#         try:
#             log_dir = self.get_log_dir()
#             if not os.path.exists(log_dir):
#                 os.makedirs(log_dir)
#
#             # Файл с текущей датой
#             today = self.get_today()
#             log_file = os.path.join(log_dir, f"server_log_{today}.txt")
#
#             # Записываем в файл
#             with open(log_file, 'a', encoding='utf-8') as f:
#                 f.write(log_entry + '\n')
#
#         except Exception as e:
#             print(f"Ошибка записи лога: {e}")
#
#     def _clean_old_logs(self):
#         """Очистка логов старше 2 недель (выполняется раз в день)"""
#         try:
#             # Проверяем, не выполняли ли очистку сегодня
#             today = datetime.now().date()
#             if hasattr(self, '_last_clean_date') and self._last_clean_date == today:
#                 return
#
#             log_dir = self.get_log_dir()
#             if not os.path.exists(log_dir):
#                 return
#
#             # Вычисляем дату 2 недели назад
#             two_weeks_ago = today - timedelta(days=14)
#
#             # Проходим по всем файлам логов
#             for filename in os.listdir(log_dir):
#                 if filename.startswith("server_log_") and filename.endswith(".txt"):
#                     # Извлекаем дату из имени файла
#                     try:
#                         date_str = filename.replace("server_log_", "").replace(".txt", "")
#                         file_date = datetime.strptime(date_str, "%d.%m.%y").date()
#
#                         # Удаляем файлы старше 2 недель
#                         if file_date < two_weeks_ago:
#                             file_path = os.path.join(log_dir, filename)
#                             os.remove(file_path)
#                             print(f"Удален старый лог: {filename}")
#
#                     except ValueError:
#                         continue  # Пропускаем файлы с некорректным именем
#
#             # Сохраняем дату последней очистки
#             self._last_clean_date = today
#
#         except Exception as e:
#             print(f"Ошибка очистки логов: {e}")
#
#     def _load_today_logs(self):
#         """Загрузка логов за текущий день при запуске"""
#         try:
#             log_dir = self.get_log_dir()
#             today = self.get_today()
#             log_file = os.path.join(log_dir, f"server_log_{today}.txt")
#
#             if os.path.exists(log_file):
#                 with open(log_file, 'r', encoding='utf-8') as f:
#                     lines = f.readlines()
#                     for line in lines:
#                         line = line.strip()
#                         if line:
#                             self.log.append(line)
#
#         except Exception as e:
#             print(f"Ошибка загрузки логов: {e}")
#
#     def initialize_logging(self):
#         """Инициализация системы логирования (вызывать при старте приложения)"""
#         # Создаем папку для логов
#         log_dir = self.get_log_dir()
#         if not os.path.exists(log_dir):
#             os.makedirs(log_dir)
#
#         # Добавляем разделитель запуска
#         timestamp = self.time_operation()
#         separator = f"{timestamp} [INFO] {'-' * 50} ЗАПУСК ПРИЛОЖЕНИЯ {'-' * 50}"
#
#
#         # Загружаем логи за сегодня
#         self._load_today_logs()
#
#         # Выполняем первоначальную очистку
#         self._clean_old_logs()
#         self.log.append(separator)