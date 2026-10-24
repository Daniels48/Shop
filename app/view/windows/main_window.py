from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyQt5.QtCore import Qt, QTimer

from app.handlers.event_handler import EventHandler
from app.presenter.main_presenter import MainPresenter
from app.view.windows.panels import LeftPanel, RightPanel, TopPanel
from app.utils.decorators import debug_decorator


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shop")
        self.resize(1920, 1080)

        self.presenter = MainPresenter(self)
        self.initUI()

        self.event_handler = EventHandler(main_window=self,presenter=self.presenter)
        self.event_handler.install()

        self.add_black_overlay()
        self.showFullScreen()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)

        # Панели
        self.top_panel = TopPanel(number_check=self.presenter.number_check,parent=self)
        self.left_panel = LeftPanel(presenter=self.presenter, parent=self)
        self.right_panel = RightPanel(presenter=self.presenter, parent=self)

        # Разделение панелей
        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.right_panel)

        main_layout.addWidget(self.top_panel)
        main_layout.addWidget(splitter)

        QTimer.singleShot(0,lambda: splitter.setSizes([int(0.8 * self.width()),int(0.2 * self.width()),]))

    def add_black_overlay(self):
        # === Добавляем затемняющий оверлей ===
        self.overlay = QWidget(self)
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 210);")  # Полупрозрачный чёрный
        self.presenter.overlay_off()

    def resizeEvent(self, event):
        """ Обновляем размер затемняющий оверлей при изменении окна"""
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    # handle event
    @debug_decorator
    def handle_key_press(self, event):
        self.event_handler.handle_key_press(event)

    def keyPressEvent(self, event):
        self.handle_key_press(event)