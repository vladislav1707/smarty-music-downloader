from core.settings import Settings
from core.proxy_manager import ProxyManager

settings = Settings()
pm = ProxyManager(settings)
proxies = pm.fetch_proxies()
print(f"Получено {len(proxies)} прокси")
for p in proxies[:5]:
    print(p)