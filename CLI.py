import argparse
import logging
import sys
# api
from api import Api
# version
from version import __version__

def main():
    # logging settings
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

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

    # downloader subparser
    downloader_parser = subparsers.add_parser("download", help="--all, --profile name")
    downloader_parser.add_argument("--all", action="store_true", help="-all")                                       # all
    downloader_parser.add_argument("--profile", metavar="NAME", help="--profile name")                              # profile


    # args
    args = parser.parse_args()

    # api
    api = Api()

    if args.command == "settings":
        if args.set:
            name, value = args.set
            api.set_setting(name, value)
            api.save_settings()
            print(f"set: {name} = {value}")
        elif args.get:
            name = args.get
            print(f"get: {name} = {api.get_setting(name)}")
        elif args.show_all:
            api.show_all_settings()
        elif args.reset:
            name = args.reset
            api.reset_setting(name)
            api.save_settings()
            print(f"reset: {name} = {api.get_setting(name)}")
        elif args.reset_all:
            confirm = input("Are you sure? (y/n): ")
            if confirm.lower() == 'y':
                api.reset_all_settings()
                api.save_settings()
                print("All settings have been reset to default.")
            else:
                print("Reset cancelled")
    elif args.command == "profile":
        if args.list:
            print(api.list_profiles())
        elif args.exists:
            name = args.exists
            print(api.profile_exists(name))
        elif args.path:
            name = args.path
            print(api.profile_path(name))
    elif args.command == "download":
        if args.all:
            api.download_all()
        elif args.profile:
            name = args.profile
            api.download_profile(name)
    else:
        print(f"not found: {args.command}, try --help")

if __name__ == "__main__":
    main()