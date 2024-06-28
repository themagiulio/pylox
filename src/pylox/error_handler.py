import sys

from pylox.token import Token
from pylox.token_type import TokenType


class ErrorHandler:
    had_error: bool = False
    had_runtime_error: bool = False

    def error(self, token: Token | int, message: str):
        if isinstance(token, Token):
            if token.token_type == TokenType.EOF:
                self.report(token.line, "", message)
            else:
                self.report(token.line, f" at '{token.lexeme}'", message)
        else:
            self.report(token, "", message)

    def report(self, line: int, where: str, message: str):
        print(f"Line {line} | Error{where}: {message}", file=sys.stderr)
        self.had_error = True
