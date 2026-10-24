import sys
import asyncio

from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop

from view.windows.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()

    with loop:
        loop.run_forever()
