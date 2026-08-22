
# TODO: перевести на английский комментарии

import yt_dlp
import time
import logging
import shutil
from static_ffmpeg import run
# core
from .profile_manager import ProfileManager
from .settings import Settings
from .proxy_rotator import ProxyRotator

# create a logger with the same name as the file (downloader)
logger = logging.getLogger(__name__)

class Downloader:
    # constructor
    def __init__(self, settings: Settings, profile_manager: ProfileManager, proxy_rotator: ProxyRotator):
        self._settings = settings
        self._profile_manager = profile_manager
        self._proxy_rotator = proxy_rotator

        # путь к ffmpeg
        self._ffmpeg_path = None
        self._ensure_ffmpeg()

    def download_profile(self, name: str):
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

        # добавить в аргументы положение ffmpeg
        if self._ffmpeg_path:
            ytdlp_args['ffmpeg_location'] = self._ffmpeg_path

        ytdlp_args["proxy"] = self._proxy_rotator.get_proxy()
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
                    with yt_dlp.YoutubeDL(ytdlp_args) as ydl:
                        ret_code = ydl.download([url])
                    if ret_code == 0:
                        logger.info("Successfully downloaded \"%s\" after %d attempt(s)", url, attempt)
                        success = True
                    else:
                        # yt-dlp завершился с ошибкой, но не выбросил исключение
                        raise Exception(f"yt-dlp returned error code {ret_code}")
                except Exception as e:
                    logger.debug(
                        "Attempt %d failed for \"%s\": %s. Retrying with next proxy...",
                        attempt, url, str(e)
                    )
                    # после ошибки сменить прокси
                    self._proxy_rotator.next_proxy()
                    ytdlp_args['proxy'] = self._proxy_rotator.get_proxy()

                    self._ensure_proxy(ytdlp_args)

                    # пауза
                    time.sleep(1)

    def download_all(self):
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


    # убедится что прокси не None (ОЧЕНЬ ВАЖНО)
    def _ensure_proxy(self, ytdlp_args: dict):
        attempts = 0
        while ytdlp_args["proxy"] is None:
            attempts += 1
            logger.info("%s | Waiting for proxies to be validated... (next check in 5s)", attempts)
            time.sleep(5)
            self._proxy_rotator.next_proxy()
            ytdlp_args["proxy"] = self._proxy_rotator.get_proxy()

    # убедится что скачан ffmpeg, и если надо скачать
    def _ensure_ffmpeg(self):
        # если уже найден путь то ничего делать не надо
        if self._ffmpeg_path:
            return
        # попробовать скачать/найти ffmpeg
        try:
            self._ffmpeg_path = run.get_ffmpeg_path()
            logger.info(f"FFmpeg ready: {self._ffmpeg_path}")
        except ImportError:
            logger.warning("static-ffmpeg not installed, please install it.")
            self._ffmpeg_path = None