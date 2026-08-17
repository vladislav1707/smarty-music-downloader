import requests
import logging
from .settings import Settings
from typing import List

# create a logger with the same name as the file (profile_manager)
logger = logging.getLogger(__name__)

class ProxyManager:
    # constructor
    def __init__(self, settings: Settings):
        self._settings = settings

        # retrieve the URL from the settings and verify that it is not empty; otherwise, trigger a critical error
        self._url = self._settings.get("proxy_url")
        if not self._url:
            logger.critical("Configuration error, \"proxy_url\" not set")
            raise SystemExit

    # return a list of proxies
    def fetch_proxies(self) -> List[str]:
        try:
            # HTTP request to the page to retrieve proxies; one proxy per line
            response = requests.get(self._url, timeout=10)
            # create a string containing the proxy text
            text_data = response.text
            # return the resulting list of proxies
            return text_data.splitlines()
        
        except requests.exceptions.Timeout:
            logger.error("Request timed out while fetching proxies")
            return []
        except requests.exceptions.HTTPError as e:
            logger.error("HTTP error: %s", e)
            return []
        except requests.exceptions.RequestException as e:
            logger.error("Request failed: %s", e)
            return []