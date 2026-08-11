import os
import json
from pathlib import Path
from typing import Any

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
    "profiles_dir": "C:/Users/lenovo/Music/Music_Folder/profiles"
    }

    # Settings class constructor
    def __init__(self):
        # if path does not exist
        if not CONFIG_PATH.exists():
            # create file and all intermediate directories, exist_ok suppresses error if file exists
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            # open file and configure: indent=4 (tab width 4 spaces), preserve non-ASCII characters
            # instead of escaping to \uXXXX
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.DEFAULTS, f, indent=4, ensure_ascii=False)
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
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=4, ensure_ascii=False) # update json file
    
    # load from file to _data (discard changes or initial load from file to _data)
    def reload(self) -> None:
        # open file and load
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        # iterate over all keys and check if each is present, if not add it
        for key, value in self.DEFAULTS.items():
            if key not in loaded:
                loaded[key] = value
        # load from file into _data
        self._data = loaded
    
    # COMPLETE reset of settings
    def reset_all(self) -> None:
        self._data = self.DEFAULTS.copy() # _data now contains a copy of default settings
    
    # reset a single setting
    def reset(self, name: str) -> None:
        # if setting does not exist, raise error about unknown setting
        if name not in self.DEFAULTS:
            raise KeyError(f"Unknown setting: {name}")
        # set setting to default value
        self._data[name] = self.DEFAULTS[name]