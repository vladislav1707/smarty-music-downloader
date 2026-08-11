# этот файл должен уметь читать профили, профиль это папка с sources.txt(список ютуб ссылок с комментариями) и ytdlp_args.json

from settings import Settings
import os
import json
from pathlib import Path
from typing import List

ROOT_DIR = Path(__file__).parent.parent   # поднимаемся на два уровня вверх

class ProfileManager:
    # конструктор класса менеджера профилей
    def __init__(self, settings: Settings):
        # сохранить настройки в приватное поле
        self._settings = settings
        # raw это путь к директории профилей
        raw = self._settings.get("profiles_dir")
        # если profile_preset то указать относительный путь к пресетам 
        if raw == "profile_presets":
            self._profiles_dir = ROOT_DIR / "profile_presets"
        # иначе указать путь как есть
        else:
            self._profiles_dir = Path(raw)

    # список ссылок в конкретном профиле
    def get_links(self, name):
        # получить ссылки(игнорируя комментарии) которые содержатся в sources.txt профиля имени name
        # и вернуть полученные ссылки в удобном формате
        pass

    # вернуть аргументы для yt-dlp
    def get_ytdlp_args(self, name):
        pass

    # вернуть список доступных профилей
    def list_profiles(self) -> List[str]:
        # если директории с профилями нету либо это не директория а файл вернуть пустой список
        if not self._profiles_dir.exists() or not self._profiles_dir.is_dir():
            return []
        # в ином случае вернуть список папок в директории с профилями, это и будет список профилей
        return [item.name for item in self._profiles_dir.iterdir() if item.is_dir()]

    # проверить существование профиля определенного в аргументе имени, возвращает bool
    def profile_exists(self, name: str) -> bool:
        # проверяет существует ли папка с именем name в директории профилей
        return self._profiles_dir.joinpath(name).exists()

    # вернуть путь к профилю, на вход принимает имя профиля
    def profile_path(self, name):
        # к _profiles_dir добавить name
        pass