import argparse
import logging
import sys
# import modules from core
from core.settings import Settings
from core.profile_manager import ProfileManager
from core.proxy_rotator import ProxyRotator
from core.downloader import Downloader
# version
from version import __version__

def main():
    # logging settings
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler('smarty_music_downloader.log', mode='w', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(message)s'))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # main parser
    parser = argparse.ArgumentParser(description="Smarty Music Downloader")
    # version
    parser.add_argument('--version', action='version', version=f'Smarty Music Downloader {__version__}')
    # subparsers
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands:")

    # settings subparser
    settings_parser = subparsers.add_parser("settings", help="--set name value, --get name, --reset name, --reset_all")
    settings_parser.add_argument("--set", nargs=2, metavar=("NAME", "VALUE"), help="--set name value")              # set
    settings_parser.add_argument("--get", metavar="NAME", help="--get name")                                        # get
    settings_parser.add_argument("--show_all", action="store_true", help="--show_all")                              # show_all
    settings_parser.add_argument("--reset", metavar="NAME", help="--reset name")                                    # reset a single setting
    settings_parser.add_argument("--reset_all", action="store_true", help="--reset_all")                            # reset_all

    # profile subparser
    profile_parser = subparsers.add_parser("profile", help="--list, --exists name, --path name, --links name, --links-all")
    profile_parser.add_argument("--list", action="store_true", help="--list")                                       # list_profiles
    profile_parser.add_argument("--exists", metavar="NAME", help="--exists name")                                   # profile_exists
    profile_parser.add_argument("--path", metavar="NAME", help="--path name")                                       # profile_path
    profile_parser.add_argument("--links", metavar="NAME", help="--links name")                                     # links
    profile_parser.add_argument("--links_all", action="store_true", help="--links_all")                             # links_all

    # downloader subparser
    downloader_parser = subparsers.add_parser("download", help="--all, --profile name")
    downloader_parser.add_argument("--all", action="store_true", help="-all")                                       # all
    downloader_parser.add_argument("--profile", metavar="NAME", help="--profile name")                              # profile


    # args
    args = parser.parse_args()

    # instance of the Settings class
    settings = Settings()

    # instance of the ProfileManager class
    profile_manager = ProfileManager(settings)

    # instance of the ProxyRotator class
    proxy_rotator = ProxyRotator(settings)

    # instance of the Downloader class
    downloader = Downloader(settings, profile_manager, proxy_rotator)

    if args.command == "settings":
        if args.set:
            name, value = args.set
            settings.set(name, value)
            settings.save()
            print(f"set: {name} = {value}")
        elif args.get:
            name = args.get
            print(f"get: {name} = {settings.get(name)}")
        elif args.show_all:
            settings.show_all()
        elif args.reset:
            name = args.reset
            settings.reset(name)
            settings.save()
            print(f"reset: {name} = {settings.get(name)}")
        elif args.reset_all:
            confirm = input("Are you sure? (y/n): ")
            if confirm.lower() == 'y':
                settings.reset_all()
                settings.save()
                print("All settings have been reset to default.")
            else:
                print("Reset cancelled")
    elif args.command == "profile":
        if args.list:
            print(profile_manager.list_profiles())
        elif args.exists:
            name = args.exists
            print(profile_manager.profile_exists(name))
        elif args.path:
            name = args.path
            print(profile_manager.profile_path(name))
        elif args.links:
            name = args.links
            print(len(profile_manager.get_links(name)))
        elif args.links_all:
            print(len(profile_manager.get_all_links()))
    elif args.command == "download":
        if args.all:
            downloader.download_all()
        elif args.profile:
            name = args.profile
            downloader.download_profile(name)
    else:
        print(f"not found: {args.command}, try --help")

if __name__ == "__main__":
    main()