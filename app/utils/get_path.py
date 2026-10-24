import sys
import os

from config import global_path_icons

def resource_path(relative_path):
    """ Получает правильный путь к ресурсам в PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)  # Для собранного приложения
    return os.path.join(os.path.abspath("."), relative_path)  # Для обычного запуска


def get_resourse_path_icon(name: str) -> str:
    raw_path = f"{global_path_icons}/{name}"
    return resource_path(raw_path)


