
# TODO: разобраться с многопоточностью, пул рабочих прокси(ДОЛЖЕН ОБНОВЛЯТЬСЯ МНОГОПОТОЧНО), разобраться с тем какие новые настройки добавить
# TODO: после завершения написания модуля перевести комментарии на английский, либо сделать исключение только для этого модуля и оставить все русским
# TODO: так как в этом модуле есть шанс что изменения будут чаще всего

import time
import logging
import requests
import threading
from threading import Thread
# core
from .proxy_manager import ProxyManager
from .settings import Settings

# create a logger with the same name as the file (proxy_rotator)
logger = logging.getLogger(__name__)

class ProxyRotator:
    def __init__(self, settings: Settings, proxy_manager: ProxyManager):
        # настройки
        self._settings = settings
        self._refresh_interval = self._settings.get("proxy_refresh_interval")

        # менеджер прокси
        self._proxy_manager = proxy_manager
        # последнее обновление списка прокси
        self._last_update = None
        # текущий выбранный прокси
        self.current_proxy = None
        # список прокси (не фильтрованных)
        self._proxy_list = proxy_manager.fetch_proxies()
        # список рабочих прокси(обновлять каждые N секунд, значение N указать в настройках)
        self.working_proxy_list = []

    # этот метод должен запустить поиск рабочих прокси(многопоточный):
    # скачать -> валидировать(многопоточно! Нужно т.к. proxifly валидирует недостаточно и 99% не работают с ютубом) -> записать в working_proxy_list
    def update_working_proxy_list(self):
        self._update_proxy()
        pass

    # меняет current_proxy на следующий в списке
    def next_proxy(self):
        pass

    # update the proxy list if needed
    def _update_proxy(self):
        if self._need_refresh() or self._current_proxy == None:
            self._proxy_list = self._proxy_manager.fetch_proxies()
            self._last_update = time.monotonic()
            if self._proxy_list:
                logger.info(f"Proxy list updated: fetched {len(self._proxy_list)} proxies")
            else:
                logger.warning("Proxy list updated: fetched 0 proxies (empty list)")

    # check if a refresh is needed
    def _need_refresh(self) -> bool:
        return (time.monotonic() - self._last_update) >= self._refresh_interval
