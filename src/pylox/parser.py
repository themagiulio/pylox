from pylox.error_handler import ErrorHandler
from pylox.token import Token
from pylox.token_type import TokenType
from pylox.expr import (
    Expr,
    Assign,
    Binary,
    Call,
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    This,
    Variable,
    Unary,
)
from pylox.stmt import (
    Stmt,
    Block,
    Break,
    Class,
    Expression,
    Function,
    If,
    Print,
    Return,
    Var,
    While,
)


class Parser:
    class ParseError(RuntimeError):
        def __init__(self, message: str | None = None):
            super().__init__(message)

    tokens: list[Token]
    current: int = 0
    loop_depth = 0
    error_handler: ErrorHandler

    def __init__(self, tokens: list[Token], error_handler: ErrorHandler):
        self.tokens = tokens
        self.error_handler = error_handler

    def parse(self) -> list[Stmt]:
        statements: list[Stmt] = []

        while not self.is_at_end():
            statements.append(self.declaration())

        return statements

    def declaration(self) -> Stmt:
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration()
            elif self.match(TokenType.VAR):
                return self.var_declaration()
            elif self.match(TokenType.FUN):
                return self.function("function")
            return self.statement()
        except Parser.ParseError:
            self.syncronize()
            return None

    def class_declaration(self) -> Class:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods: list[Function] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function("method"))

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return Class(name, methods)

    def statement(self) -> Stmt:
        if self.match(TokenType.FOR):
            return self.for_statement()

        if self.match(TokenType.IF):
            return self.if_statement()

        if self.match(TokenType.PRINT):
            return self.print_statement()

        if self.match(TokenType.RETURN):
            return self.return_statement()

        if self.match(TokenType.WHILE):
            return self.while_statement()

        if self.match(TokenType.BREAK):
            return self.break_statement()

        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())

        return self.expression_statement()

    def for_statement(self):
        try:
            self.loop_depth += 1

            self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
            initializer: Stmt | None = None
            condition: Expr | None = None
            increment: Expr | None = None

            if self.match(TokenType.SEMICOLON):
                initializer = None
            elif self.match(TokenType.VAR):
                initializer = self.var_declaration()
            else:
                initializer = self.expression_statement()

            if not self.check(TokenType.SEMICOLON):
                condition = self.expression()

            self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

            if not self.check(TokenType.RIGHT_PAREN):
                increment = self.expression()

            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

            body: Stmt = self.statement()

            if increment is not None:
                body = Block([body, Expression(increment)])

            if condition is None:
                condition = Literal(True)

            body = While(condition, body)

            if initializer is not None:
                body = Block([initializer, body])

            return body
        finally:
            self.loop_depth -= 1

    def if_statement(self) -> If:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch: Stmt = self.statement()
        else_branch: Stmt | None = None

        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return If(condition, then_branch, else_branch)

    def print_statement(self) -> Print:
        value: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def return_statement(self) -> Return:
        keyword: Token = self.previous()
        value: Expr = None

        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)

    def var_declaration(self) -> Var:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer: Expr = None

        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def while_statement(self) -> While:
        try:
            self.loop_depth += 1

            self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
            condition: Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
            body: Stmt = self.statement()

            return While(condition, body)
        finally:
            self.loop_depth -= 1

    def break_statement(self) -> Break:
        if self.loop_depth == 0:
            self.error_handler.error(
                self.previous(), "Must be inside a loop to use 'break'."
            )

        self.consume(TokenType.SEMICOLON, "Expect ';' after 'break'.")
        return Break()

    def expression_statement(self) -> Stmt:
        expr: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)

    def function(self, kind: str) -> Function:
        name: Token = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        params: list[Token] = []

        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                params.append(
                    self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                )
                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body: list[Stmt] = self.block()

        return Function(name, params, body)

    def block(self) -> list[Stmt]:
        stmts: list[Stmt] = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            stmts.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return stmts

    def expression(self) -> Expr:
        return self.assignment()

    def assignment(self):
        expr: Expr = self.logic_or()

        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr = self.assignment()

            if isinstance(expr, Variable):
                name: Token = expr.name
                return Assign(name, value)
            elif isinstance(expr, Get):
                return Set(expr.object, expr.name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

    def logic_or(self) -> Expr:
        expr: Expr = self.logic_and()

        while self.match(TokenType.OR):
            operator: Token = self.previous()
            right: Expr = self.logic_and()
            expr = Logical(expr, operator, right)

        return expr

    def logic_and(self) -> Expr:
        expr: Expr = self.equality()

        while self.match(TokenType.AND):
            operator: Token = self.previous()
            right: Expr = self.equality()
            expr = Logical(expr, operator, right)

        return expr

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

        return self.call()

    def finish_call(self, callee: Expr) -> Expr:
        args: list[Expr] = []

        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                args.append(self.expression())

                if not self.match(TokenType.COMMA):
                    break

        paren: Token = self.consume(
            TokenType.RIGHT_PAREN, "Expect ')' after arguments."
        )

        return Call(callee, paren, args)

    def call(self) -> Expr:
        expr: Expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name: Token = self.consume(
                    TokenType.IDENTIFIER,
                    "Expect property name after '.'.",
                )
                expr = Get(expr, name)
            else:
                break

        return expr

    def primary(self):
        if self.match(TokenType.FALSE):
            return Literal(False)

        if self.match(TokenType.TRUE):
            return Literal(True)

        if self.match(TokenType.NIL):
            return Literal(None)

        if self.match(TokenType.THIS):
            return This(self.previous())

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())

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
        return Parser.ParseError(message)

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def is_at_end(self):
        return self.peek().token_type == TokenType.EOF
