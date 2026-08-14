import argparse
import sys
import logging
from pathlib import Path
# import modules from core
from core.settings import Settings
from core.profile_manager import ProfileManager

def main():
    # logger
    logger = logging.getLogger(__name__)

    # main parser
    parser = argparse.ArgumentParser(description="Smarty Music Downloader")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # settings subparser
    settings_parser = subparsers.add_parser("settings", help="--set name value, --get name, --reset name, --reset_all")
    settings_parser.add_argument("--set", nargs=2, metavar=("NAME", "VALUE"), help="--set name value")  # set
    settings_parser.add_argument("--get", metavar="NAME", help="--get name")                            # get
    settings_parser.add_argument("--reset", metavar="NAME", help="--reset name")                        # reset a single setting
    settings_parser.add_argument("--reset_all", action="store_true", help="--reset_all")                # reset all

    # args
    args = parser.parse_args()

    if args.command == "settings":
        # instance of the settings class
        settings = Settings()

        if args.set:
            name, value = args.set
            settings.set(name, value)
            settings.save()
            print(f"set: {name} = {value}")
        elif args.get:
            name = args.get
            print(f"get: {name} = {settings.get(name)}")
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
        else:
            print(f"not found: {args.command}, try --help")
            



if __name__ == "__main__":
    main()