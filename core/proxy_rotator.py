
# TODO: перевод комментов на английский

import time
import logging
import requests
import socks
import threading
import queue
from urllib.parse import urlparse
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
        self._cleanup_interval = self._settings.get("proxy_cleanup_interval")
        self._max_validation_threads = self._settings.get("max_validation_threads")

        # менеджер прокси
        self._proxy_manager = ProxyManager(self._settings)
        # последнее обновление списка прокси
        self._last_update = 0
        # последняя очистка списка рабочих прокси
        self._last_cleanup = 0
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

    def next_proxy(self) -> None:
        """Меняет current_proxy на следующий в списке рабочих прокси, пропуская нерабочие"""
        # берём прокси из списка под блокировкой
        with self.locker:
            # если есть прокси то переключится на него, иначе вывести предупреждение что прокси не найдены
            if self.working_proxy_list:
                self.current_proxy = self.working_proxy_list.pop(0)
                logger.info(f"Switched to proxy: {self.current_proxy}")
            else:
                self.current_proxy = None
                logger.warning("No working proxies available")

    def get_proxy(self) -> str:
        """Просто вернет текущий прокси"""
        # блокировка на всякий случай
        with self.locker:
            return self.current_proxy

    def _update_working_proxy_list(self):
        """Этот метод нужен чтобы создать воркеры и управлять ими"""
        # создать заданное в настройках количество потоков для валидации прокси    
        for i in range(self._max_validation_threads):
            threading.Thread(target=self._worker_loop, daemon=True).start()
        # бесконечный цикл: скачать список -> сделать очередь чтобы не портить _proxy_list
        while True:
            # обновить список прокси если надо
            self._update_proxy_list()
            self._cleanup_working_proxy_list()
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

    def _worker_loop(self):
        """Метод для воркеров. Содержит бесконечный цикл"""
        proxy = None
        # если сейчас запущена проверка
        while True:
            # записать в переменную proxy из self._validation_queue последний прокси и удалить из списка
            try:
                proxy = self._validation_queue.get(timeout=1.0)
            except queue.Empty:
                continue
            # валидация
            logger.info("Proxy validation: %s", proxy)
            if self._validate(proxy):
                with self.locker:
                    self.working_proxy_list.append(proxy)
                logger.info("Proxy validation was successful: %s", proxy)
            self._validation_queue.task_done()

    def _update_proxy_list(self):
        """Update the proxy list if needed"""
        if self._need_refresh() or self.current_proxy == None:
            self._proxy_list = self._proxy_manager.fetch_proxies()
            self._last_update = time.monotonic()
            if self._proxy_list:
                logger.info(f"Proxy list updated: fetched {len(self._proxy_list)} proxies")
            else:
                logger.warning("Proxy list updated: fetched 0 proxies (empty list)")

    def _need_refresh(self) -> bool:
        """Check if a refresh is needed"""
        return (time.monotonic() - self._last_update) >= self._refresh_interval

    def _validate(self, proxy: str) -> bool:
        """Проверить только 1 прокси на работоспособность"""
        try:
            # если прокси socks5 или socks4
            if proxy.startswith(('socks5://', 'socks4://')):
                # распарсить на протокол, хост и порт
                parsed = urlparse(proxy)
                # если нет хоста или порта то прокси не рабочий
                if not parsed.hostname or not parsed.port:
                    return False
                # записать тип прокси(SOCKS5 или SOCKS4)
                proxy_type = socks.SOCKS5 if proxy.startswith('socks5://') else socks.SOCKS4
                # Создаём SOCKS-сокет и пытаемся подключиться к YouTube
                sock = socks.socksocket()
                # установить прокси
                sock.set_proxy(proxy_type, parsed.hostname, parsed.port)
                # таймаут
                sock.settimeout(5)
                # попытка подключится
                sock.connect(('www.youtube.com', 443))
                # закрыть сокет
                sock.close()
                return True
            # HEAD-запрос с отключенной проверкой SSL
            response = requests.head(
                "https://www.youtube.com/",             # тестовый URL
                proxies={                               # настройки прокси
                    "http": proxy,
                    "https": proxy,
                },
                timeout=(3, 5),                        # таймауты
                verify=False,                           # отключить лишние проверки
                allow_redirects=True                    # разрешаем редиректы
            )
            # успешный статус (2xx или даже 3xx)
            return response.status_code < 400
        except Exception as e:
            logger.debug(f"Proxy {proxy} validation error: {e}")  
            # любая ошибка = прокси не работает
            return False

    def _cleanup_working_proxy_list(self):
        """Очистить список рабочих прокси если надо"""
        with self.locker:
            if self._cleanup_interval > 0 and (time.monotonic() - self._last_cleanup) >= self._cleanup_interval:
                self.working_proxy_list = []
        