from settings import Settings

s = Settings()
s.reset_all
print("max_working_proxies:", s.get("max_working_proxies"))
print("proxy_provider:", s.get("proxy_provider"))
print("profiles_dir:", s.get("profiles_dir"))