from pylox.token_type import TokenType


class Token:
    token_type: TokenType
    lexeme: str
    line: int
    literal: object | None

    def __init__(
        self,
        token_type: TokenType,
        lexeme: str,
        literal: object | None,
        line: int,
    ):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        return f"{self.token_type} {self.lexeme} {self.literal}"
