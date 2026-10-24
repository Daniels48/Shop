import subprocess
import os
from PyQt5.QtCore import QSize, QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

program_path = r'C:\SC552\LoadParm.exe'


class PaymentThread(QThread):
    # Сигнал для передачи результата оплаты
    payment_result_signal = pyqtSignal(int)

    def __init__(self, args):
        super().__init__()
        self.args = args

    def run(self):
        """Запуск процесса оплаты в потоке."""
        exit_code = self.execute_payment(self.args)
        self.payment_result_signal.emit(exit_code)

    def execute_payment(self, args):
        """Запуск внешнего процесса для обработки оплаты."""
        process = subprocess.Popen([program_path, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit_code = process.wait()
        return exit_code


def check_valid_terminal(self):
    """Запуск процесса проверки доступности терминала."""
    args = ["26", "1"]
    process = subprocess.run([program_path] + args, stdout=True, stderr=True, text=True)
    exit_code = process.returncode

    valid = False

    if exit_code == 99:
        valid = False
        space = " " * 11
        message = f"{space}Терминал оплаты не подключен!\n\nПереподключите терминал и попробуйте заново."
        QMessageBox.warning(self, "Ошибка",message, QMessageBox.Ok)
    elif exit_code != 0:
        valid = False
        QMessageBox.warning(self, "Ошибка", f"Ошибка в терминале оплаты: exit_code: {exit_code}", QMessageBox.Ok)
    elif exit_code == 0:
        valid = True

    return valid





