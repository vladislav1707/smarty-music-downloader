# этот файл должен уметь читать профили, профиль это папка с sources.txt(список ютуб ссылок с комментариями) и ytdlp_args.json

from settings import Settings
import os
import json
from pathlib import Path
from typing import List

class ProfileManager:
    # конструктор класса менеджера профилей
    def __init__(self, settings: Settings):
        # сохранить ссылку на настройки
        self.settings = settings

    # вывести текущую директорию с профилями
    def _get_profiles_dir(self) -> Path:
        # получить директорию с профилями из настроек
        profiles_dir = self.settings.get("profiles_dir")
        # если нету то выдать ошибку
        if profiles_dir is None:
            raise ValueError("The 'profiles_dir' setting is not specified in settings.json.")
        # вернуть директорию с профилями
        return Path(profiles_dir)

    # список ссылок в конкретном профиле
    def get_links(self, name):
        # получить ссылки(игнорируя комментарии) которые содержатся в sources.txt профиля имени name
        # и вернуть полученные ссылки в удобном формате
        pass
    
    def get_ytdlp_args(self, name):
        pass

    # вернуть список доступных профилей
    def list_profiles(self) -> List[str]:
        # перечислить доступные профили(в папке профилей) которая была получена в конструкторе класса и вернуть в удобном формате
        profiles_dir = self._get_profiles_dir()
        # если директории с профилями нету либо это не директория а файл вернуть пустой список
        if not profiles_dir.exists() or not profiles_dir.is_dir():
            return []
        # в ином случае вернуть список папок в директории с профилями, это и будет список профилей
        return [item.name for item in profiles_dir.iterdir() if item.is_dir()]

    # проверить существование профиля определенного в аргументе имени, возвращает bool
    def profile_exists(self, name: str) -> bool:
        # проверяет существует ли папка с именем name в директории профилей
        return self._get_profiles_dir().joinpath(name).exists()