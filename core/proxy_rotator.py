import time
import logging
import requests
from .proxy_manager import ProxyManager
from .settings import Settings

# create a logger with the same name as the file (proxy_rotator)
logger = logging.getLogger(__name__)

class ProxyRotator:
    def __init__(self, settings: Settings):
        # settings
        self._settings = settings
        self._refresh_interval = self._settings.get("proxy_refresh_interval")
        # proxy_manager
        self._proxy_manager = ProxyManager(self._settings)

        self._last_update = 0.0
        self._proxy_list = []
        self._current_proxy = None

    # check if a refresh is needed
    def _need_refresh(self) -> bool:
        return (time.monotonic() - self._last_update) >= self._refresh_interval

    # update the proxy list if needed
    def _update_proxy(self):
        if self._need_refresh():
            self._proxy_list = self._proxy_manager.fetch_proxies()
            self._last_update = time.monotonic()
            if self._proxy_list:
                logger.info("Proxy list updated: fetched %s proxies", len(self._proxy_list))
            else:
                logger.warning("Proxy list updated: fetched 0 proxies (empty list)")

    # switch to the next proxy
    def next_proxy(self):
        counter = 0
        while True:
            counter += 1

            self._update_proxy()

            # take the last proxy from the list as the current one and remove it
            if self._proxy_list != []:
                self._current_proxy = self._proxy_list.pop()
                logger.info("%s | attempt to switch proxy: %s", counter, self._current_proxy)
            # if there are no proxies in the list, wait for an update
            else:
                logger.info("No proxies available, waiting for refresh...")
                time.sleep(10)
                continue

            if self._is_proxy_working(self._current_proxy):
                logger.info("Working proxy found: %s", self._current_proxy)
                return
    
    # get the current proxy
    def get_proxy(self) -> str:
        self._update_proxy()
        return self._current_proxy

    # checking if the proxy is working
    def _is_proxy_working(self, proxy: str) -> bool:
        if proxy is None:
            return false
        try:
            # It might be a SOCKS proxy, not just HTTP/HTTPS
            requests.get(
                "https://www.youtube.com",
                proxies={"http": proxy, "https": proxy},
                timeout=(1, 2)
            )
            return True
        except Exception:
            return False