from pylox.token import Token
from pylox.expr import Expr


class Stmt:
    pass


class Expression(Stmt):
    expression: Expr

    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)


class Print(Stmt):
    expression: Expr

    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_print_stmt(self)


class Var(Stmt):
    name: Token
    initializer: Expr

    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        return visitor.visit_var_stmt(self)
