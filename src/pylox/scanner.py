from pylox.error_handler import ErrorHandler
from pylox.token_type import TokenType
from pylox.token import Token


class Scanner:
    source: str
    tokens: list[str] = []
    start: int = 0
    current: int = 0
    line: int = 1
    error_handler: ErrorHandler

    keywords = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
    }

    def __init__(self, source: str, error_handler: ErrorHandler):
        self.source = source
        self.error_handler = error_handler

    def scan_tokens(self) -> list[str]:
        self.tokens = []

        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        c: str = self.advance()

        match c:
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case ",":
                self.add_token(TokenType.COMMA)
            case ".":
                self.add_token(TokenType.DOT)
            case "-":
                self.add_token(TokenType.MINUS)
            case "+":
                self.add_token(TokenType.PLUS)
            case ";":
                self.add_token(TokenType.SEMICOLON)
            case "*":
                # Check if a multiline comment is ending
                if self.match("/"):
                    self.advance()
                else:
                    self.add_token(TokenType.STAR)
            case "!":
                self.add_token(
                    TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG
                )
            case "=":
                self.add_token(
                    TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL
                )
            case "<":
                self.add_token(
                    TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS
                )
            case ">":
                self.add_token(
                    TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER
                )
            case "/":
                # Check if a comment is beginning
                if self.match("/"):
                    while self.peek() != "\n" and not self.is_at_end():
                        self.advance()
                elif self.match("*"):
                    while self.peek() != "*" and not self.is_at_end():
                        self.advance()
                else:
                    self.add_token(TokenType.SLASH)
            case " " | "\r" | "\t":
                # Ignore whitespaces
                return
            case "\n":
                self.line += 1
            case '"':
                self.string()
            case _:
                if c.isnumeric():
                    self.number()
                elif c.isalpha():
                    self.identifier()
                else:
                    self.error_handler.error(self.line, "Unexpected character.")

        return

    def advance(self):
        c = self.source[self.current]
        self.current += 1
        return c

    def peek(self, lookahead: int = 0):
        if self.current + lookahead >= len(self.source):
            return "\0"
        return self.source[self.current + lookahead]

    def match(self, expected: str):
        if self.is_at_end():
            return False

        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            # Increase line counter fo multi-line strings
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.is_at_end():
            self.error_handler.error(self.line, "Unterminated string.")
            return

        # Closing '"'
        self.advance()

        # Trim surrounding quotes
        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self):
        while self.peek().isnumeric():
            self.advance()

        # Look for a fractional part
        if self.peek() == "." and self.peek(lookahead=1).isnumeric():
            # Consume the "."
            self.advance()

            while self.peek().isnumeric():
                self.advance()

        self.add_token(TokenType.NUMBER, float(self.source[self.start : self.current]))

    def identifier(self):
        while self.peek().isalnum():
            self.advance()

        # Check if is user-defined identifier
        text = self.source[self.start : self.current]
        token_type: TokenType | None = self.keywords.get(text, None)

        if token_type is None:
            token_type = TokenType.IDENTIFIER

        self.add_token(token_type)

    def add_token(self, token_type: TokenType, literal: object | None = None):
        text = self.source[self.start : self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def is_at_end(self):
        return self.current >= len(self.source)
