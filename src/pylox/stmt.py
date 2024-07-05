from pylox.token import Token
from pylox.expr import Expr, Variable


class Stmt:
    pass


class Block(Stmt):
    statements: list[Stmt]

    def __init__(self, statements):
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_block_stmt(self)


class Break(Stmt):
    def accept(self, visitor):
        return visitor.visit_break_stmt(self)


class Expression(Stmt):
    expression: Expr

    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)


class Function(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt]

    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor):
        return visitor.visit_function_stmt(self)


class Class(Stmt):
    name: Token
    superclass: Variable
    methods: list[Function]

    def __init__(self, name, superclass, methods):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def accept(self, visitor):
        return visitor.visit_class_stmt(self)


class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None

    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor):
        return visitor.visit_if_stmt(self)


class Print(Stmt):
    expression: Expr

    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_print_stmt(self)


class Return(Stmt):
    keyword: Token
    value: Expr

    def __init__(self, keyword, value):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor):
        return visitor.visit_return_stmt(self)


class Var(Stmt):
    name: Token
    initializer: Expr

    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        return visitor.visit_var_stmt(self)


class While(Stmt):
    condition: Expr
    body: Stmt

    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def accept(self, visitor):
        return visitor.visit_while_stmt(self)
