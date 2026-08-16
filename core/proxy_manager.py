import requests
import logging
from .settings import Settings
from typing import List

# create a logger with the same name as the file (profile_manager)
logger = logging.getLogger(__name__)

class ProxyManager:
    # вернуть скачанный список прокси
    def get_proxies(self, settings: Settings) -> List[str]:
        # получить url из настроек
        url = settings.get("proxy_url")
        # HTTP-запрос на страницу чтобы получить прокси, 1 строка 1 прокси
        response = requests.get(url, timeout=10)
        # создать строку с текстом содержащим прокси
        text_data = response.text
        # вернуть список прокси который получился
        return text_data.splitlines()