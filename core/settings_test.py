from settings import Settings

s = Settings()

print("format:", s.get("format"))
s.set("format", "mp3")
print("after set:", s.get("format"))
s.save()
print("saved")
s.reload()
print("after reload:", s.get("format"))
