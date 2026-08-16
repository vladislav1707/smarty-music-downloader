from core.settings import Settings
from core.proxy_manager import ProxyManager

settings = Settings()
pm = ProxyManager()
proxies = pm.get_proxies(settings)
print(f"Получено {len(proxies)} прокси")
for p in proxies[:5]:
    print(p)