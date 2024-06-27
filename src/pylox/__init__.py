import sys

from pylox.pylox import PyLox


def main():
    pylox: PyLox = PyLox()
    file_path: str | None = None

    try:
        file_path = sys.argv[1]
    except IndexError:
        file_path = None

    if file_path is None:
        pylox.run_prompt()
    else:
        pylox.run_file(file_path)
