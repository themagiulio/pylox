import sys

from pylox.pylox import PyLox


def main():
    file_path: str | None = None

    try:
        file_path = sys.argv[1]
    except IndexError:
        file_path = None

    PyLox(file_path)
