# TODO: перевести на английский и добавить в документацию

from .profile_manager import ProfileManager
from .settings import Settings
from .proxy_rotator import ProxyRotator
import yt_dlp
import time
import logging

# create a logger with the same name as the file (downloader)
logger = logging.getLogger(__name__)

class Downloader:
    # constructor
    def __init__(self, settings: Settings, profile_manager: ProfileManager, proxy_rotator: ProxyRotator):
        self._settings = settings
        self._profile_manager = profile_manager
        self._proxy_rotator = proxy_rotator

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
                        ydl.download([url])
                    logger.info("Successfully downloaded \"%s\" after %d attempt(s)", url, attempt)
                    success = True
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

    # убедится что прокси не None
    def _ensure_proxy(self, ytdlp_args: dict):
        while ytdlp_args['proxy'] is None:
            logger.warning("No proxy available, waiting 5 seconds...")
            time.sleep(5)
            self._proxy_rotator.next_proxy()
            ytdlp_args['proxy'] = self._proxy_rotator.get_proxy()