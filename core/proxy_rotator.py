from proxy_manager import ProxyManager
from settings import Settings

class ProxyRotator:
    def __init__(self, settings: Settings):
        self._settings = settings