Attention: the translation into English was made by AI, the original version in [Russian](README.ru.md)

# Table of Contents
- [Table of Contents](#table-of-contents)
- [What is this and why do you need it?](#what-is-this-and-why-do-you-need-it)
- [Installation](#installation)
  - [Windows](#windows)
  - [Linux](#linux)
  - [Mac OS](#mac-os)
- [Quick Start](#quick-start)
  - [Downloading](#downloading)
- [Important (to avoid getting banned by YouTube)](#important-to-avoid-getting-banned-by-youtube)
- [Settings](#settings)
  - [Where to change settings](#where-to-change-settings)
  - [Available settings](#available-settings)
  - [Profile System](#profile-system)
  - [What is a profile?](#what-is-a-profile)
  - [How to create a profile](#how-to-create-a-profile)
- [CLI Commands](#cli-commands)
  - [Miscellaneous](#miscellaneous)
  - [Settings](#settings-1)
  - [Profiles](#profiles)
  - [Downloading](#downloading-1)
- [GUI Limitations](#gui-limitations)
- [Credits](#credits)
- [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)
  - [How do I add download links?](#how-do-i-add-download-links)
  - [GUI sucks, where are the settings?](#gui-sucks-where-are-the-settings)
  - [Why do I need another interface for yt-dlp?](#why-do-i-need-another-interface-for-yt-dlp)
  - [Slow download speed](#slow-download-speed)

# What is this and why do you need it?

The project uses the [MIT License](LICENSE).

**Brief description:**  
This program is designed to mass‑download music/video from YouTube using `yt-dlp`. It is completely free and open source. It features a unique **profile system** and **proxy rotation**. **Despite the name, video downloading is also supported.**

**Important:** this program makes sense for long‑term use. If you have only a few files, it will slow you down, **BUT** if you have huge playlists and many links, it will help a lot because it bypasses temporary IP bans and error 429.

**Features:**
* Built‑in proxy validation (VERY FAST).

* Proxies are rotated on each error (bypasses temporary IP bans from YouTube).

* Profile system (different links with different arguments).

* A working GUI (RAW).

* You can configure folder‑based sorting (per profile).

* This project is open source and COMPLETELY FREE.

* If you don't like something or find something missing, you can add it yourself. For example, paint everything pink by modifying the code, or add new buttons. A simple change – switch the theme from `clam` to `alt`.

* If a video is deleted after you've downloaded it, it won't disappear from your library.

* Several ready‑to‑use profile presets are included.

* Both audio and video downloads are supported.

# Installation

## Windows
Just download the latest archive from the Releases page and extract it anywhere you like. Inside you'll find two executable files: GUI and CLI. **The CLI version is more complete, and I recommend using that one.**

## Linux
1. Make sure Python 3.8 or higher is installed.
2. Download the source code, navigate to the folder containing `CLI.py` and `GUI.py`.
3. Run with `python` or `python3`:
   * `python CLI.py --help` – shows the list of CLI commands.
   * `python GUI.py` – launches the GUI version.
4. If you want to run it quickly, you can add an alias or come up with something else.

> If you'd like to extend these instructions, feel free to contact me.

## Mac OS
The process is the same as for Linux, but if something doesn't work, try installing FFmpeg via Homebrew:
```brew install ffmpeg```

# Quick Start

Right after installation, I strongly recommend configuring the program to your needs: create your own profiles based on the presets, or rename and move the presets folder and set a global path in the settings.

## Downloading
If you use the GUI, to download links from all profiles with their respective arguments, you'll need to press the big **DOWNLOAD ALL** button.

# Important (to avoid getting banned by YouTube)

**Please!** Do not add your own cookies to the arguments (`ytdlp_args.json`), otherwise you might get banned on YouTube!

# Settings

In the settings you can change things like `profiles_dir`, number of threads for downloading, and similar. If you're looking for where to change `yt-dlp` options or add download links, see the [Profile System](#profile-system) section.

## Where to change settings
Either via CLI, or manually in the `data/settings.json` file.

## Available settings
* `proxy_url` – link to a raw proxy list (default uses SOCKS5 proxies from proxifly).
* `profiles_dir` – the directory where profiles are searched.
* `proxy_refresh_interval` – how often the proxy list is downloaded from the internet (default every 5 minutes and 5 seconds).
* `proxy_cleanup_interval` – how often the working proxy list is cleaned up (needed due to very fast validation; set to `0` to disable cleanup).
* `max_validation_threads` – number of threads used for proxy validation (recommended not to change).

## Profile System

All profiles **MUST** be in a single directory (folder), otherwise the program won't see them. You can specify that directory in the settings (parameter `profiles_dir`). If you set it to `"profile_presets"`, the program will use the bundled presets folder – this is the default.

## What is a profile?
Profiles contain links and arguments. Links from a profile are downloaded with that profile's arguments. Arguments from other profiles do not apply to this profile and vice versa.

## How to create a profile
You can create a profile, for example, from a preset: simply copy it to your profiles directory, rename it as you like, write your links into `sources.txt` (and optional comments), and if you think it's necessary, change the arguments in `ytdlp_args.json`.

# CLI Commands

**Note:** examples are for Windows. If you're on Linux, just replace `SMDownloader_CLI.exe` with `python CLI.py` or your alias – everything will work the same.

> To see the full list of all commands, run `SMDownloader_CLI.exe --help`.

## Miscellaneous
* `SMDownloader_CLI.exe --help` – show command list.
* `SMDownloader_CLI.exe --version` – show version.

## Settings
* `SMDownloader_CLI.exe settings --show_all` – show all settings.
* `SMDownloader_CLI.exe settings --set "parameter" "value"` – change a setting.
* `SMDownloader_CLI.exe settings --get "parameter"` – display the value of a parameter.

## Profiles
* `SMDownloader_CLI.exe profiles --list` – list found profiles.
* `SMDownloader_CLI.exe profiles --exists "name"` – check if a profile exists.
* `SMDownloader_CLI.exe profiles --path "name"` – show the path to a profile.
* `SMDownloader_CLI.exe profiles --links_all` – show the total number of links.

## Downloading
* `SMDownloader_CLI.exe download --all` – process links from all profiles.
* `SMDownloader_CLI.exe download --profile "name"` – process links only from one profile.

# GUI Limitations

**Currently the GUI does NOT support:**
* creating and editing profiles (only viewing);
* editing settings (this is available in CLI);
* processing only 1 profile at a time (this is available in CLI).

# Credits
I made this project alone. Should I thank myself? Well, okay:
Mister Smarty Pants – lead coder, designer, etc.

# Frequently Asked Questions (FAQ)

## How do I add download links?
First, you need a profile. You can use presets or create a profile based on a preset:
1. `music_opus` – profile for downloading music in opus format. If you need mp3, you can base your profile on this one.
2. `video_mp4` – profile for downloading video in mp4 format.

Decided on a profile / created your own? Great! Here's how to add links to a profile:
1. Find `sources.txt` or create it if it doesn't exist in the profile.
2. Write your links (one link per line).
3. Optionally add comments (a comment occupies the whole line and starts with `#`).

## GUI sucks, where are the settings?
You can configure the program via CLI or manually in `data/settings.json`. The GUI is raw and has no settings editor yet.

## Why do I need another interface for yt-dlp?
The main purpose of this project is not the interface, but **proxy rotation**. The program automatically switches proxies on errors, helping to bypass blocks. There is also a CLI version in addition to the GUI.

## Slow download speed
It may be slow because free proxies are used by default. I've optimised the validation to squeeze as much as possible out of free proxies. In the long run, it's not that slow thanks to bypassing error 429 (Too many requests). If you need to download a few thousand files (like I do), this project is fine. But if you only have a few files to download, this project is not worth it.