from core.settings import Settings
from core.profile_manager import ProfileManager
from core.proxy_rotator import ProxyRotator
from core.downloader import Downloader
from typing import List, Any
import logging

# Create a logger with the same name as the file (api)
logger = logging.getLogger(__name__)

class Api:
    def __init__(self) -> None:
        """Constructor"""
        self._settings = Settings()
        self._profile_manager = ProfileManager(self._settings)
        self._proxy_rotator = None
        self._downloader = None

    # settings management

    def set_setting(self, name: str, value: str) -> None:
        """Set the setting. Requires save_settings()"""
        self._settings.set(name, value)

    def get_setting(self, name: str) -> Any:
        """Get the setting"""
        return self._settings.get(name)

    def save_settings(self) -> None:
        """Apply changes and save settings to the configuration file"""
        self._settings.save()

    def reload_settings(self) -> None:
        """The opposite of save, useful for cancellation"""
        self._settings.reload()

    def reset_setting(self, name: str) -> None:
        """Reset single setting. Requires save_settings()"""
        self._settings.reset(name)

    def reset_all_settings(self) -> None:
        """Reset all settings. Requires save_settings()"""
        self._settings.reset_all()

    def show_all_settings(self) -> None:
        """Print all settings"""
        self._settings.show_all()

    # profile management

    def list_profiles(self) -> List[str]:
        """Returns a list containing all the names of the profiles found"""
        return self._profile_manager.list_profiles()

    def profile_exists(self, name: str) -> bool:
        """Check if the profile exists"""
        return self._profile_manager.profile_exists(name)

    def profile_path(self, name: str) -> str:
        """Return the path to the profile"""
        return str(self._profile_manager.profile_path(name))

    def get_total_links_count(self) -> int:
        """Return total links count"""
        return self._profile_manager.get_total_links_count()

    def get_downloaded_links(self) -> int:
        """Return downloaded links count"""
        return self._downloader.get_downloaded_links()

    def get_profile_links(self, name: str):
        """Get list of downloaded links for a specific profile"""
        return self._profile_manager.get_links(name)

    # download operations

    def download_profile(self, name: str) -> None:
        """Download single profile"""
        self._start()
        self._downloader.download_profile(name)

    def download_all(self) -> None:
        """Download all profiles"""
        self._start()
        self._downloader.download_all()

    def _start(self):
        """Create an instance of ProxyRotator and Downloader"""
        if self._proxy_rotator is None and self._downloader is None:
            self._proxy_rotator = ProxyRotator(self._settings)
            self._downloader = Downloader(
                        self._settings,
                        self._profile_manager,
                        self._proxy_rotator
                    )