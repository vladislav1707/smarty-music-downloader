import yt_dlp
import time
import logging
import os
import sys
from pathlib import Path

# create a logger with the same name as the file (downloader)
logger = logging.getLogger(__name__)

# настройка кэша для ffmpeg

# если windows
if sys.platform == "win32":
    # добавить путь
    cache_dir = Path(os.environ.get("APPDATA", os.path.expanduser("~"))) / "SmartyMusicDownloader" / "ffmpeg_cache"
# иначе
else:
    # добавить другой путь
    cache_dir = Path.home() / ".cache" / "smarty_music_downloader" / "ffmpeg"

cache_dir.mkdir(parents=True, exist_ok=True)
os.environ["STATIC_FFMPEG_DIR"] = str(cache_dir)

# импортировать ffmpeg после установки переменной окружения
import static_ffmpeg
# попробовать скачать/проверить наличие ffmpeg
try:
    static_ffmpeg.add_paths()
# если ошибка то выйти с программы и вывести сообщение
except Exception as e:
    logger.critical("Failed to download/initialize ffmpeg: %s", e)
    raise SystemExit("FFmpeg is required for this application.")

# core
from .profile_manager import ProfileManager
from .settings import Settings
from .proxy_rotator import ProxyRotator

class _ErrorCapturingYDL(yt_dlp.YoutubeDL):
    """YoutubeDL, но который записывает ошибки

    вместо игнорирования ошибок либо прерывания из-за ошибок собирает список ошибок
    """

    def __init__(self, *args, **kwargs):
        """Инициализация. Принимает аргументы и передает в __init__ родительского класса"""
        super().__init__(*args, **kwargs)
        # список возникших ошибок
        self.error_messages: list[str] = []

    def report_error(self, message, *args, **kwargs):
        """вызывается в YoutubeDL когда что-то пошло не так"""
        
        # если есть аргументы то:
        if args:
            # попытаться подставить в сообщение аргументы
            try:
                formatted = message % args
            # при ошибке оставить просто сообщение
            except Exception:
                formatted = message
        # если аргументов нет то оставить сообщение как есть и ничего не подставлять
        else:
            formatted = message

        # добавить в список ошибок ошибку
        self.error_messages.append(str(formatted))
        # вызвать report_error из родительского класса(yt_dlp.YoutubeDL) чтобы поведение осталось как есть
        super().report_error(message, *args, **kwargs)

class _RetryableError(Exception):
    """свое исключение для ситуаций когда надо повторить попытку"""
    pass

class Downloader:
    # список ошибок при которых не надо повторять попытку скачивания
    PERMANENT_ERROR_MARKERS = (
        "private video",
        "this video is private",
        "video unavailable",
        "this video is not available",
        "this video has been removed",
        "removed by the uploader",
        "removed by uploader",
        "this video has been deleted",
        "deleted video",
        "this video is no longer available",
        "account associated with this video has been terminated",
        "the uploader has not made this video available",
        "no video formats found",
        "unsupported url",
        "sign in to confirm your age",
        "premieres in",
        "will premiere",
    )
    
    def __init__(self, settings: Settings, profile_manager: ProfileManager, proxy_rotator: ProxyRotator):
        """Constructor"""
        self._settings = settings
        self._profile_manager = profile_manager
        self._proxy_rotator = proxy_rotator

        # обработанные ссылки
        self._downloaded_links = 0

    def download_profile(self, name: str):
        """Download single profile"""
        # 1. проверить что профиль существует, если нет то ошибка
        if not self._profile_manager.profile_exists(name):
            logger.error("profile %s not found", name)
            return

        # 2. получить список ссылок и аргументы профиля
        ytdlp_args = self._profile_manager.get_ytdlp_args(name)
        links = self._profile_manager.get_links(name)
        if not links:
            logger.warning("Profile \"%s\" contains no links", name)
            return
        
        # передать прокси
        ytdlp_args["proxy"] = self._proxy_rotator.get_proxy()
        # убедится что прокси не None
        self._ensure_proxy(ytdlp_args)

        # 3. для каждой ссылки в профиле скачать с помощью yt-dlp и подставить аргументы из профиля
        for url in links:
            success = False
            attempt = 0
            # пытаться пока не получится
            while not success:
                attempt += 1

                # попытаться обработать ссылку, при неудаче сменить прокси
                try:
                    # попытка скачивания
                    with _ErrorCapturingYDL(ytdlp_args) as ydl:
                        ret_code = ydl.download([url])
                    if ret_code == 0:
                        logger.info("Successfully downloaded \"%s\" after %d attempt(s)", url, attempt)
                        success = True
                    else:
                        # собрать ошибки которые были проигнорированы
                        errors = ydl.error_messages

                        # если есть ошибки:
                        if errors:
                            # список перманентных ошибок(только булевые значения)
                            permanent_errors_list = []
                            # для каждой ошибки в списке ошибок:
                            for error in errors:
                                # добавить булевое значение в список permanent_errors_list. True если ошибка перманентная, иначе False
                                permanent_errors_list.append(self._is_permanent_error(error))
                            # если все ошибки перманентные и больше повторять смысла нет:
                            if all(permanent_errors_list):
                                # вывести предупреждение
                                logger.warning(
                                "Some items in \"%s\" could not be downloaded (permanent errors): %s",
                                url, "; ".join(errors)
                                )
                                # прервать цикл
                                break

                        # выбросить исключение _RetryableError (свое). {'; '.join(errors)} склеивает все ошибки в 1 строку используя ; как разделители
                        raise _RetryableError(f"yt-dlp returned error code {ret_code}: {'; '.join(errors)}")
                except Exception as e:
                    # проверить что ошибка не перманентная, если перманентная выйти из цикла и вывести сообщение в лог
                    # эта часть при обычных условиях не так нужна, она нужна когда ignoreerrors=False и в еще некоторых особых ситуациях
                    # not isinstance(e, _RetryableError) проверяет что e не экземпляр класса _RetryableError
                    if not isinstance(e, _RetryableError) and self._is_permanent_error(e):
                        logger.warning("Error \"%s\" occurred on link \"%s\", skipped", e, url)
                        break
                        
                    logger.debug(
                        "Attempt %d failed for \"%s\": %s. Retrying with next proxy...",
                        attempt, url, e
                    )
                    # после ошибки сменить прокси
                    self._proxy_rotator.next_proxy()
                    ytdlp_args["proxy"] = self._proxy_rotator.get_proxy()

                    self._ensure_proxy(ytdlp_args)

                    # пауза
                    time.sleep(1)
            self._downloaded_links += 1

    def download_all(self):
        """Download all profiles"""
        # сбросить счетчик ссылок перед скачиванием
        self._downloaded_links = 0
        # сохранить список профилей
        profiles = self._profile_manager.list_profiles()
        # если профилей нет то warning и конец выполнения функции
        if not profiles:
            logger.warning("No profiles found in profiles_dir")
            return
        # пройтись по всем профилям и для каждого из них:
        for i in range(len(profiles)):
            name = profiles[i]
            try:
                self.download_profile(name)
                logger.info("Profile \"%s\" processed successfully", name)
            except Exception as e:
                logger.error("Failed to process profile \"%s\": %s", name, str(e))

    def _ensure_proxy(self, ytdlp_args: dict):
        """Убедится что прокси не None (ОЧЕНЬ ВАЖНО)"""
        attempts = 0
        while ytdlp_args["proxy"] is None:
            attempts += 1
            logger.info("%s | Waiting for proxies to be validated... (next check in 5s)", attempts)
            time.sleep(5)
            self._proxy_rotator.next_proxy()
            ytdlp_args["proxy"] = self._proxy_rotator.get_proxy()

    def _is_permanent_error(self, exc: Exception | str) -> bool:
        """Проверить что ошибка не исправится сменой прокси и повторной попыткой"""
        text = str(exc).lower()
        # для каждого маркера перманентной ошибки
        for marker in self.PERMANENT_ERROR_MARKERS:
            # проверить наличие в тексте, если есть True, иначе False
            if marker in text:
                return True
        return False

    def get_downloaded_links(self) -> int:
        return self._downloaded_links