import sys

from pylox.error_handler import ErrorHandler
from pylox.scanner import Scanner
from pylox.parser import Parser
from pylox.expr import Expr


class PyLox:
    error_handler: ErrorHandler = ErrorHandler()

    def run_file(self, file_path: str) -> None:
        pass

    def run_prompt(self) -> None:
        print("Pylox, an implementation of the Lox programming language.")

        while True:
            line = str(input(">>> "))
            self.run(line)
            self.error_handler.had_error = False

    def run(self, source):
        scanner: Scanner = Scanner(source, self.error_handler)
        tokens: list[str] = scanner.scan_tokens()
        parser: Parser = Parser(tokens, self.error_handler)

        # Stop if there was a syntax error
        if self.error_handler.had_error:
            sys.exit(65)

        from pylox.ast_printer import AstPrinter

        expression: Expr = parser.parse()

        print(AstPrinter().print(expression))

    def report(self, line: int, message: str) -> None:
        print(f"[{line}] Error: {message}")


if __name__ == "__main__":
    print("ciao")
