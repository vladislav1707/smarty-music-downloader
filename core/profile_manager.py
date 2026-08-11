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

    # список ссылок для скачивания в конкретном профиле
    def get_links(self, name: str) -> List[str]:
        # получить расположение sources.txt в профиле
        sources_file = self.profile_path(name) / "sources.txt"
        # список ссылок
        links = []

        # если нету sources.txt тогда вернуть пустой список
        if not sources_file.exists():
            return []

        # открыть sources_file в режиме чтения("r") и в utf-8
        with open(sources_file, "r", encoding="utf-8") as f:
            # для каждой линии в файле
            for line in f:
                # убрать пробельные символы в начале и конце строки
                line = line.strip()
                # если строка не пустая и не комментарий добавить в список ссылок
                if line and not line.startswith("#"):
                    links.append(line)

        # вернуть список ссылок
        return links

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
    def profile_path(self, name: str) -> Path:
        # к _profiles_dir добавить name(имя профиля)
        return self._profiles_dir / name