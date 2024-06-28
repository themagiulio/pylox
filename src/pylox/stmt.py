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
