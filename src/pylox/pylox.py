import sys
import readline  # noqa: F401

from pylox.error_handler import ErrorHandler
from pylox.scanner import Scanner
from pylox.parser import Parser
from pylox.interpreter import Interpreter
from pylox.stmt import Stmt


class PyLox:
    error_handler: ErrorHandler = ErrorHandler()

    def run_file(self, file_path: str) -> None:
        source: str = ""

        try:
            with open(file_path, "r") as f_obj:
                source = f_obj.read()
        except IOError:
            # HACK, should use error_handler instead
            print(f"Error: No such file or directory '{file_path}'.")
            self.error_handler.had_error = True

        self.run(source)

        if self.error_handler.had_runtime_error or self.error_handler.had_error:
            sys.exit(70)

    def run_prompt(self) -> None:
        print(
            "Pylox, an implementation of the Lox programming language written in Python."
        )

        try:
            while True:
                line = str(input(">>> "))
                self.run(line)
                self.error_handler.had_error = False
                self.error_handler.had_runtime_error = False
        except KeyboardInterrupt:
            print("\nExited pylox\n")
            exit()

    def run(self, source):
        scanner: Scanner = Scanner(source, self.error_handler)
        tokens: list[str] = scanner.scan_tokens()
        parser: Parser = Parser(tokens, self.error_handler)
        interpreter: Interpreter = Interpreter(self.error_handler)

        stmts: list[Stmt] = parser.parse()

        # Stop if there was a syntax error
        if self.error_handler.had_error or self.error_handler.had_runtime_error:
            return

        interpreter.interpret(stmts)

    def report(self, line: int, message: str) -> None:
        print(f"[{line}] Error: {message}")


if __name__ == "__main__":
    print("ciao")
