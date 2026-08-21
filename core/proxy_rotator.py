
# TODO: разобраться с многопоточностью, пул рабочих прокси(ДОЛЖЕН ОБНОВЛЯТЬСЯ МНОГОПОТОЧНО), разобраться с тем какие новые настройки добавить
# TODO: после завершения написания модуля перевести комментарии на английский, либо сделать исключение только для этого модуля и оставить все русским
# TODO: так как в этом модуле есть шанс что изменения будут чаще всего

import time
import logging
import requests
import threading
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
        self._max_validation_threads = self._settings.get("max_validation_threads")

        # менеджер прокси
        self._proxy_manager = proxy_manager
        # последнее обновление списка прокси
        self._last_update = None
        # текущий выбранный прокси
        self.current_proxy = None
        # список прокси (не фильтрованных)
        self._proxy_list = proxy_manager.fetch_proxies()
        # очередь прокси
        self.validation_queue = None
        # список рабочих прокси(обновлять каждые N секунд, значение N указать в настройках)
        self.working_proxy_list = []

        # запустить автообновление списка рабочих прокси в другом потоке
        threading.Thread(target=self._update_working_proxy_list, daemon=True).start()

    # меняет current_proxy на следующий в списке рабочих прокси
    def next_proxy(self):
        pass

    # этот метод должен запустить поиск рабочих прокси(многопоточный):
    # скачать -> валидировать(многопоточно! Нужно т.к. proxifly валидирует недостаточно и 99% не работают с ютубом) -> записать в working_proxy_list
    def _update_working_proxy_list(self):
        while True:
            # обновить список прокси если надо
            self._update_proxy_list()
            # коопировать список прокси для удобства
            self.validation_queue = self._proxy_list.copy()
            # создать заданное в настройках количество потоков для валидации прокси
            for i in range(self._max_validation_threads):
                threading.Thread(target=self._worker_loop, daemon=True).start()

    # Брать из очереди прокси и проверять в бесконечном цикле. Нужно предусмотреть отключение потоков когда они не нужны но не удаление.
    # Этот метод нужен для потоков проверки прокси
    def _worker_loop(self):
        pass

    # update the proxy list if needed
    def _update_proxy_list(self):
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

    # проверить только 1 прокси на работоспособность
    def _validate(self, proxy: str):
        try:
            # HEAD-запрос с отключенной проверкой SSL
            response = requests.head(
                "https://www.youtube.com/robots.txt",   # тестовый URL
                proxies={                               # настройки прокси
                    "http": proxy,
                    "https": proxy,
                },
                timeout=(3, 5),                         # таймауты: 3 сек на соединение, 5 сек на чтение
                verify=False,                           # отключить лишние проверки
                allow_redirects=True                    # разрешаем редиректы
            )
            # успешный статус (2xx или даже 3xx)
            return response.status_code < 400
        except:
            # любая ошибка = прокси не работает
            return False
        