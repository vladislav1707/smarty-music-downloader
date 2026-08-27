# core/path_utils.py
import sys
from pathlib import Path

def get_root_dir() -> Path:
    """
    Определяет корневую директорию проекта.
    Если .exe то как есть, если разработка то на 2 директории выше
    """
    if getattr(sys, 'frozen', False):
        # запущено как собранный EXE
        if hasattr(sys, '_MEIPASS'):
            # Режим --onefile
            return Path(sys._MEIPASS)
        else:
            # Режим --onedir
            return Path(sys.executable).parent
    else:
        # На 2 уровня вверх
        return Path(__file__).parent.parent