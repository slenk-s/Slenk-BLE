"""src/main.py"""

from src.app import BLEApplication


def main():
    app = BLEApplication()
    app.run()


if __name__ == "__main__":
    main()