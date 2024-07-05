from typing import Final
from enum import Enum, auto

from pylox.error_handler import ErrorHandler
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
    Unary,
)
from pylox.interpreter import Interpreter
from pylox.stmt import (
    Stmt,
    Block,
    Class,
    Expression,
    Function,
    If,
    Print,
    Return,
    Var,
    While,
)
from pylox.token import Token
from pylox.visitor import Visitor


class Resolver(Visitor):
    interpreter: Final[Interpreter]
    scopes: list[dict[str, bool]]
    error_handler: ErrorHandler

    class FunctionType(Enum):
        NONE = auto()
        FUNCTION = auto()
        INITIALIZER = auto()
        METHOD = auto()

    class ClassType(Enum):
        NONE = auto()
        CLASS = auto()

    current_function: FunctionType = FunctionType.NONE
    current_class: ClassType = ClassType.NONE

    def __init__(self, interpreter: Interpreter, error_handler):
        self.interpreter = interpreter
        self.error_handler = error_handler
        self.scopes = []

    def visit_block_stmt(self, stmt: Block):
        self.begin_scope()
        self.resolve_stmts(stmt.statements)
        self.end_scope()

    def visit_class_stmt(self, stmt: Class):
        enclosing_class = self.current_class
        self.current_class = Resolver.ClassType.CLASS

        self.declare(stmt.name)
        self.define(stmt.name)

        self.begin_scope()
        self.scopes[-1]["this"] = True

        for method in stmt.methods:
            declaration = Resolver.FunctionType.METHOD

            if method.name.lexeme == "init":
                declaration = Resolver.FunctionType.INITIALIZER

            self.resolve_function(method, declaration)

        self.end_scope()
        self.current_class = enclosing_class

    def visit_expression_stmt(self, stmt: Expression):
        self.resolve(stmt.expression)

    def visit_function_stmt(self, stmt: Function):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, Resolver.FunctionType.FUNCTION)

    def visit_if_stmt(self, stmt: If):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)

        if stmt.else_branch is not None:
            self.resolve(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print):
        self.resolve(stmt.expression)

    def visit_return_stmt(self, stmt: Return):
        if self.current_function == Resolver.FunctionType.NONE:
            self.error_handler.error(
                stmt.keyword,
                "Can't return from top-level code.",
            )

        if stmt.value is not None:
            if self.current_function == Resolver.FunctionType.INITIALIZER:
                self.error_handler.error(
                    stmt.keyword, "Can't return a value from an initializer."
                )
            self.resolve(stmt.value)

    def visit_var_stmt(self, stmt: Var):
        self.declare(stmt.name)

        if stmt.initializer is not None:
            self.resolve(stmt.initializer)

        self.define(stmt.name)

    def visit_while_stmt(self, stmt: While):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visit_assign_expr(self, expr: Assign):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_binary_expr(self, expr: Binary):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_call_expr(self, expr: Call):
        self.resolve(expr.callee)

        for arg in expr.arguments:
            self.resolve(arg)

    def visit_get_expr(self, expr: Get):
        self.resolve(expr.object)

    def visit_grouping_expr(self, expr: Grouping):
        self.resolve(expr.expression)

    def visit_literal_expr(self, expr: Literal):
        return

    def visit_logical_expr(self, expr: Logical):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_set_expr(self, expr: Set):
        self.resolve(expr.value)
        self.resolve(expr.object)

    def visit_this_expr(self, expr: This):
        if self.current_class == Resolver.ClassType.NONE:
            return self.error_handler.error(
                expr.keyword, "Can't use 'this' outside of a class."
            )
        self.resolve_local(expr, expr.keyword)

    def visit_unary_expr(self, expr: Unary):
        self.resolve(expr.right)

    def visit_variable_expr(self, expr: Expr):
        if self.scopes and self.scopes[-1].get(expr.name.lexeme) is False:
            self.error_handler.error(
                expr.name, "Can't read local variable in its own initializer."
            )

        self.resolve_local(expr, expr.name)

    def resolve(self, expr_or_stmt: Expr | Stmt | list[Expr] | list[Stmt]):
        if isinstance(expr_or_stmt, list):
            for stmt in expr_or_stmt:
                self.resolve(stmt)
            return

        expr_or_stmt.accept(self)

    def resolve_function(
        self,
        function: Function,
        function_type: FunctionType,
    ):
        enclosing_function: Resolver.FunctionType = self.current_function
        self.current_function = function_type
        self.begin_scope()

        for param in function.params:
            self.declare(param)
            self.define(param)

        self.resolve(function.body)
        self.end_scope()
        self.current_function = enclosing_function

    def resolve_stmts(self, stmts: list[Stmt]):
        for stmt in stmts:
            self.resolve(stmt)

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: Token):
        if not self.scopes:
            return

        scope = self.scopes[-1]

        if name.lexeme in scope:
            self.error_handler.error(
                name,
                "Already a variable with this name in this scope.",
            )

        scope[name.lexeme] = False

    def define(self, name: Token):
        if not self.scopes:
            return

        self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expr: Expr, name: Token):
        for i, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, i)
