# TODO: сделать docstring

import json
import logging
from pathlib import Path
from typing import Any

# Create a logger with the same name as the file (settings)
logger = logging.getLogger(__name__)

# BASE_DIR stores the location info of the project/core. .parent is an attribute holding the parent directory
BASE_DIR = Path(__file__).parent
# BASE_DIR.parent is the project root directory. The / operator in pathlib is overloaded for paths,
# works cross-platform
CONFIG_PATH = BASE_DIR.parent / "data" / "settings.json"

class Settings:
    # default settings
    DEFAULTS = {
    "max_working_proxies": 5,
    "proxy_provider": "github_free_proxy_list",
    "profiles_dir": "profile_presets" # "profile_presets" is a special value that points to presets
    }

    # Settings class constructor
    def __init__(self):
        # if path does not exist
        if not CONFIG_PATH.exists():
            logger.warning("Settings.json file not found, attempting to create it")
            # create file and all intermediate directories, exist_ok suppresses error if file exists
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            # open file and configure: indent=4 (tab width 4 spaces), preserve non-ASCII characters
            # instead of escaping to \uXXXX
            try:
                with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump(self.DEFAULTS, f, indent=4, ensure_ascii=False)
            except (json.JSONDecodeError, PermissionError, OSError) as e:
                logger.critical("Failed to create settings from %s: %s", CONFIG_PATH, e)
                raise SystemExit
        # load settings from file into _data (dictionary on which operations are performed)
        self.reload()
    
    # read a setting (getter)
    def get(self, name: str) -> Any:
        return self._data.get(name)

    # change a setting (setter)
    def set(self, name: str, value: Any) -> None:
        self._data[name] = value
    
    # write _data to file (persist changes)
    def save(self) -> None:
        # The 'with' statement ensures proper resource cleanup. Open config file for writing.
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4, ensure_ascii=False) # update json file
            logger.info("Settings saved to %s", CONFIG_PATH)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError, OSError) as e:
            logger.error("Failed to save settings from %s: %s", CONFIG_PATH, e)

    # load from file to _data (discard changes or initial load from file to _data)
    def reload(self) -> None:
        try:
            # open file and load
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                loaded = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError, OSError) as e:
            logger.error("Failed to load settings from %s: %s", CONFIG_PATH, e)
            loaded = {}
        # iterate over all keys and check if each is present, if not add it
        for key, value in self.DEFAULTS.items():
            if key not in loaded:
                loaded[key] = value
                logger.info("Setting %s to default value: %s", key, value)
        # load from file into _data
        self._data = loaded
    
    # COMPLETE reset of settings
    def reset_all(self) -> None:
        self._data = self.DEFAULTS.copy() # _data now contains a copy of default settings
        logger.warning("Settings.json is COMPLETELY reset to default settings")
    
    # reset a single setting
    def reset(self, name: str) -> None:
        # if setting does not exist, raise error about unknown setting
        if name in self.DEFAULTS:
            # set setting to default value
            self._data[name] = self.DEFAULTS[name]
            logger.info("Setting %s to default value: %s", name, self.DEFAULTS[name])
        else:
            # if not in DEFAULTS delete setting
            self._data.pop(name)
        