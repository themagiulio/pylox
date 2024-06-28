from pylox.error_handler import ErrorHandler
from pylox.token import Token
from pylox.token_type import TokenType
from pylox.expr import Expr, Binary, Unary, Literal, Grouping


class Parser:
    class ParseError(RuntimeError):
        def __init__(self, message: str | None = None):
            super().__init__(message)

    tokens: list[Token]
    current: int = 0
    error_handler: ErrorHandler

    def __init__(self, tokens: list[Token], error_handler: ErrorHandler):
        self.tokens = tokens
        self.error_handler = error_handler

    def parse(self):
        try:
            return self.expression()
        except Parser.ParseError:
            return None

    def expression(self) -> Expr:
        return self.equality()

    def equality(self) -> Expr:
        expr: Expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self.previous()
            right: Expr = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        expr: Expr = self.term()

        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator: Token = self.previous()
            right: Expr = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        expr: Expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self.previous()
            right: Expr = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        expr: Expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self.previous()
            right: Expr = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right: Expr = self.unary()
            return Unary(operator, right)

        return self.primary()

    def primary(self):
        if self.match(TokenType.FALSE):
            return Literal(False)

        if self.match(TokenType.TRUE):
            return Literal(True)

        if self.match(TokenType.NIL):
            return Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PAREN):
            expr: Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        raise self.error(self.peek(), "Expect expression.")

    def syncronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().token_type == TokenType.SEMICOLON:
                return

            match self.peek().token_type:
                case (
                    TokenType.CLASS
                    | TokenType.FUN
                    | TokenType.VAR
                    | TokenType.FOR
                    | TokenType.IF
                    | TokenType.WHILE
                    | TokenType.PRINT
                    | TokenType.RETURN
                ):
                    return

            self.advance()

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1

        return self.previous()

    def match(self, *args: TokenType) -> bool:
        for token_type in args:
            if self.check(token_type):
                self.advance()
                return True

        return False

    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False

        return self.peek().token_type == token_type

    def consume(self, token_type: TokenType, message: str):
        if self.check(token_type):
            return self.advance()

        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str):
        self.error_handler.error(token, message)
        return Parser.ParseError()

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def is_at_end(self):
        return self.peek().token_type == TokenType.EOF
