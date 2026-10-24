import sys
import asyncio
from pathlib import Path

from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop

from app.view.windows.main_window import MainWindow


print("Исполняемый файл:", sys.executable)
print("Рабочая директория:", Path.cwd())
print("Папка ресурсов PyInstaller:", getattr(sys, "_MEIPASS", "Нет"))
print("Путь к main.py:", __file__)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()

    with loop:
        loop.run_forever()
