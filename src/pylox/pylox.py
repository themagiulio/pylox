import sys

from pylox.scanner import Scanner


class PyLox:
    had_error: bool = False

    def run_file(self, file_path: str) -> None:
        pass

    def run_prompt(self) -> None:
        print("Pylox, an implementation of the Lox programming language.")

        while True:
            line = str(input(">>> "))
            self.run(line)
            self.had_error = False

    def run(self, source):
        scanner: Scanner = Scanner(source)
        tokens: list[str] = scanner.scan_tokens()

        for token in tokens:
            print(token)

        if self.had_error:
            sys.exit(65)

    def report(self, line: int, message: str) -> None:
        print(f"[{line}] Error: {message}")


if __name__ == "__main__":
    print("ciao")
