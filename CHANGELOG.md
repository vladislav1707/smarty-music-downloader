# [3.0.2] - 2026-09-13
## Added
- Increased download speed
- Permanent errors moved to a separate python file
## Fixed
- Playlists no longer fail as a whole when the proxy dies mid-download.
  Previously, a single dead proxy could stall the entire playlist because
  proxy rotation only kicked in after the whole list finished. Now each
  item is downloaded separately, with proxy rotation per item

# [3.0.1] - 2026-09-11
## Fixed
- Improved compatibility with Linux
- Fixed a bug due to which the program could get stuck in an eternal loop during loading if a private video came across
- Removed music_opus profile from presets for easier development
- Fixed permanent errors not being detected when downloading playlists:
  the original yt-dlp error is now captured and inspected, so playlists
  with a private or unavailable item are skipped instead of retrying forever.

# [3.0.0] - 2026-08-24
**First public pre-release**

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

# Future plans

- Docker image.