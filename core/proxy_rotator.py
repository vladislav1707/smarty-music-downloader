import time
import logging
from proxy_manager import ProxyManager
from settings import Settings

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

    # проверка на то что требуется обновление
    def _need_refresh(self) -> bool:
        return (time.monotonic() - self._last_update) >= self._refresh_interval

    # если требуется обновление то обновить список прокси
    def _update_proxy(self):
        if self._need_refresh() or self._current_proxy == None:
            self._proxy_list = self._proxy_manager.fetch_proxies()
            self._last_update = time.monotonic()

    # сменить прокси на следующий
    def next_proxy(self):
        self._update_proxy()
        # выбрать последний элемент списка прокси в качестве текущего прокси а так же удалить его
        if self._proxy_list != []:
            self._current_proxy = self._proxy_list.pop()
    
    # получить текущий прокси
    def get_proxy(self):
        self._update_proxy()
        return self._current_proxy