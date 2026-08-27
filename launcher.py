import sys

def main():
    # если есть аргументы то CLI
    if len(sys.argv) > 1:
        from CLI import main as cli_main
        cli_main()
    # иначе GUI
    else:
        from GUI import main as gui_main
        gui_main()

if __name__ == "__main__":
    main()