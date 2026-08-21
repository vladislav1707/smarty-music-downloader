
# TODO: перевод комментов на английский/сделать исключение оставить на русском
# TODO: исправить документацию с учетом изменений
# TODO: сделать next_proxy() и get_proxy()

import time
import logging
import requests
import socks
import threading
import queue
# core
from .proxy_manager import ProxyManager
from .settings import Settings

# create a logger with the same name as the file (proxy_rotator)
logger = logging.getLogger(__name__)

class ProxyRotator:
    def __init__(self, settings: Settings):
        # настройки
        self._settings = settings
        self._refresh_interval = self._settings.get("proxy_refresh_interval")
        self._max_validation_threads = self._settings.get("max_validation_threads")

        # менеджер прокси
        self._proxy_manager = ProxyManager(self._settings)
        # последнее обновление списка прокси
        self._last_update = 0
        # текущий выбранный прокси
        self.current_proxy = None
        # список прокси (не фильтрованных)
        self._proxy_list = self._proxy_manager.fetch_proxies()
        # очередь прокси
        self._validation_queue = queue.Queue()
        for proxy in self._proxy_list:
            self._validation_queue.put(proxy)
        # список рабочих прокси(обновлять каждые N секунд, значение N указать в настройках)
        self.working_proxy_list = []
        # блокировщик
        self.locker = threading.Lock()

        # запустить автообновление списка рабочих прокси в другом потоке
        threading.Thread(target=self._update_working_proxy_list, daemon=True).start()

    # меняет current_proxy на следующий в списке рабочих прокси, пропуская нерабочие
    def next_proxy(self):
        # берём прокси из списка под блокировкой
        with self.locker:
            # если прокси нет то текущий прокси = None
            if not self.working_proxy_list:
                self.current_proxy = None
                return
            # взять прокси из начала списка
            proxy = self.working_proxy_list.pop(0)

        # проверка ВНЕ блокировки (это долгая операция)
        if self._validate(proxy):
            with self.locker:
                self.current_proxy = proxy
        else:
            # если не работает то повторить попытку с помощью рекурсии
            self.next_proxy()

    # просто вернет текущий прокси
    def get_proxy(self) -> str:
        # блокировка на всякий случай
        with self.locker:
            return self.current_proxy

    # этот метод должен запустить поиск рабочих прокси(многопоточный):
    # скачать -> валидировать(многопоточно! Нужно т.к. proxifly валидирует недостаточно и 99% не работают с ютубом) -> записать в working_proxy_list
    def _update_working_proxy_list(self):
        # создать заданное в настройках количество потоков для валидации прокси    
        for i in range(self._max_validation_threads):
            threading.Thread(target=self._worker_loop, daemon=True).start()
        # бесконечный цикл: скачать список -> сделать очередь чтобы не портить _proxy_list
        while True:
            # обновить список прокси если надо
            self._update_proxy_list()
            # обновление очереди прокси
            with self.locker:   # чтобы воркеры не читали во время очистки
                while not self._validation_queue.empty():
                    try:
                        # попытка очистить список
                        self._validation_queue.get_nowait()
                    except queue.Empty:
                        break
                for proxy in self._proxy_list:
                    self._validation_queue.put(proxy)
            time.sleep(self._refresh_interval)

    # Брать из очереди прокси и проверять в бесконечном цикле. Нужно предусмотреть отключение потоков когда они не нужны но не удаление.
    # Этот метод нужен для потоков проверки прокси
    def _worker_loop(self):
        proxy = None
        # если сейчас запущена проверка
        while True:
            # записать в переменную proxy из self._validation_queue последний прокси и удалить из списка
            try:
                proxy = self._validation_queue.get(timeout=1.0)
            except queue.Empty:
                continue
            # валидация
            logger.info("proxy validation: %s", proxy)
            if self._validate(proxy):
                with self.locker:
                    self.working_proxy_list.append(proxy)
                logger.info("proxy validation was successful: %s", proxy)
            self._validation_queue.task_done()

    # update the proxy list if needed
    def _update_proxy_list(self):
        if self._need_refresh() or self.current_proxy == None:
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
    def _validate(self, proxy: str) -> bool:
        try:
            # HEAD-запрос с отключенной проверкой SSL
            response = requests.head(
                "https://www.youtube.com/robots.txt",   # тестовый URL
                proxies={                               # настройки прокси
                    "http": proxy,
                    "https": proxy,
                },
                timeout=(3, 5),                        # таймауты: 3 сек на соединение, 5 сек на чтение
                verify=False,                           # отключить лишние проверки
                allow_redirects=True                    # разрешаем редиректы
            )
            # успешный статус (2xx или даже 3xx)
            return response.status_code < 400
        except Exception as e:
            logger.debug(f"Proxy {proxy} validation error: {e}")  
            # любая ошибка = прокси не работает
            return False
        