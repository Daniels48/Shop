import sys
from pathlib import Path

from app.config import global_path_icons, global_path_audio, global_path_resorces


def resource_path(relative_path: str) -> str:

    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parents[2]

    return str(base_path / relative_path)


def get_resourse_path_icon(name: str) -> str:
    return resource_path(f"{global_path_icons}/{name}")


def get_resourse_path_audio(name: str) -> str:
    return resource_path(f"{global_path_audio}/{name}")

icon_path = get_resourse_path_icon("delete.ico")
print("Путь к иконке:", icon_path)
print("Файл существует:", Path(icon_path).exists())
"""Возвращает путь к ресурсу в исходном или собранном приложении."""