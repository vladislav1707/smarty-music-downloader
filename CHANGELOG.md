# Changelog

## [3.0.0] - 2026-08-24

**First public release.**

Despite the version number 3.0.0, this is the first publicly available version. The two previous major versions (1.x and 2.x) were private and never published.

This release includes the basic functionality required for downloading music and videos from supported sites (YouTube, SoundCloud, etc.):

- Full-featured GUI with terminal‑style interface.
- Profile system – each profile can have its own yt‑dlp arguments and a list of links (`sources.txt`).
- Proxy rotation – automatically switches proxy on errors to avoid temporary IP bans.
- Multi‑threaded downloading – the interface stays responsive during downloads.
- Progress bar with spinner animation.
- Built‑in viewer for `sources.txt` files.
- CLI tool for managing settings.
- Logging to a file for debugging.

---

## Future plans

- Automatic scheduled downloads.
- Docker image.