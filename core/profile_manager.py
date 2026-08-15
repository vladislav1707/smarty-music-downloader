# TODO: сделать docstring

from .settings import Settings
import os
import json
import logging
from pathlib import Path
from typing import List

# Create a logger with the same name as the file (profile_manager)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent # go up two levels

class ProfileManager:
    # class constructor for the profile manager
    def __init__(self, settings: Settings):
        # store settings in a private field
        self._settings = settings
        # raw is the path to the profiles directory
        raw = self._settings.get("profiles_dir")
        # if profile_preset, use a relative path to the presets
        if raw == "profile_presets":
            self._profiles_dir = ROOT_DIR / "profile_presets"
            logger.warning(
                "Using default profile_presets directory: %s\n"
                "This is fine for testing, but for production use:\n"
                "  - Copy presets to a separate folder (e.g., 'my_profiles')\n"
                "  - Set 'profiles_dir' in settings.json to that path\n"
                "  - See README.md for details.",
                self._profiles_dir
            )
        # otherwise use the path as given
        else:
            self._profiles_dir = Path(raw)

    # get list of download links for a specific profile
    def get_links(self, name: str) -> List[str]:
        # get the location of sources.txt inside the profile
        sources_file = self.profile_path(name) / "sources.txt"
        links = []

        # if sources.txt does not exist, return an empty list
        if not sources_file.exists():
            logger.warning("No links in \"%s\" profile", name)
            return []

        try:
            # open sources_file in read mode ("r") with utf-8 encoding
            with open(sources_file, "r", encoding="utf-8") as f:
                # for each line in the file
                for line in f:
                    # strip whitespace from both ends
                    line = line.strip()
                    # if the line is not empty and not a comment, add to links
                    if line and not line.startswith("#"):
                        links.append(line)
        except (PermissionError, OSError) as e:
            logger.error("Failed to open %s: %s", sources_file, e)
        except (UnicodeDecodeError) as e:
            logger.error("UnicodeDecodeError in %s: %s", sources_file, e)
        return links

    # return yt-dlp arguments as a dictionary
    def get_ytdlp_args(self, name: str) -> dict:
        # get the location of ytdlp_args.json
        args_file = self.profile_path(name) / "ytdlp_args.json"
        # if the file does not exist, return an empty dict
        if not args_file.exists():
            logger.critical("ytdlp_args.json not found for profile \"%s\"", name)
            raise SystemExit
        # open the file in read mode ("r") with utf-8 encoding
        try:
            with open(args_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, PermissionError, OSError) as e:
            logger.critical("Failed to open from %s: %s", args_file, e)
            raise SystemExit

    # return a list of available profiles
    def list_profiles(self) -> List[str]:
        # if the profiles directory does not exist or is not a directory, return empty list
        if not self._profiles_dir.exists() or not self._profiles_dir.is_dir():
            return []
        # otherwise, return the names of all subdirectories in the profiles directory
        profiles = [item.name for item in self._profiles_dir.iterdir() if item.is_dir()]
        logger.info("Found %d profiles", len(profiles))
        return profiles

    # check whether a profile with the given name exists, returns bool
    def profile_exists(self, name: str) -> bool:
        return self._profiles_dir.joinpath(name).exists()

    # return the path to the profile, takes the profile name as input
    def profile_path(self, name: str) -> Path:
        # append the profile name to _profiles_dir
        return self._profiles_dir / name
    