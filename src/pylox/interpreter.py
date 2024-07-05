from typing import Final

from pylox.visitor import Visitor
from pylox.environment import Environment
from pylox.error_handler import ErrorHandler
from pylox.expr import (
    Expr,
    Assign,
    Binary,
    Call,
    Get,
    Literal,
    Logical,
    Grouping,
    Set,
    This,
    Unary,
    Variable,
)
from pylox.lox_callable import LoxCallable
from pylox.lox_class import LoxClass
from pylox.lox_exceptions import LoxReturnException
from pylox.lox_instance import LoxInstance
from pylox.lox_function import LoxFunction
from pylox.runtime_error import LoxRuntimeError
from pylox.stmt import Stmt, Block, Break, Class, Function, Return, Var, If, While
from pylox.token import Token
from pylox.token_type import TokenType


class Interpreter(Visitor):
    error_handler: ErrorHandler
    _globals: Final[Environment] = Environment()
    _locals: Final[dict[Expr, int]]
    environment: Environment = _globals
    is_repl: bool

    class Clock(LoxCallable):
        def __init__(self):
            from time import time

            super().__init__()
            self.start_time = time()

        @property
        def arity(self):
            return 0

        def call(self):
            from time import time

            return time() - self.start_time

        def __str__(self):
            return "<native fn>"

    _globals.define("clock", Clock())

    class LoxBreakException(RuntimeError):
        pass

    def __init__(self, error_handler: ErrorHandler, is_repl: bool = False):
        self.error_handler = error_handler
        self.is_repl = is_repl
        self._locals = {}

    def interpret(self, stmts: list[Stmt]):
        try:
            for stmt in stmts:
                self.execute(stmt)
        except LoxRuntimeError as err:
            self.error_handler.runtime_error(err)

    def execute(self, stmt: Stmt):
        stmt.accept(self)

    def resolve(self, expr: Expr, depth: int):
        self._locals[expr] = depth

    def execute_block(self, stmts: list[Stmt], environment: Environment):
        previous = self.environment

        try:
            self.environment = environment

            for stmt in stmts:
                self.execute(stmt)
        finally:
            self.environment = previous

    def visit_block_stmt(self, stmt: Block) -> None:
        self.execute_block(stmt.statements, Environment(self.environment))
        return None

    def visit_class_stmt(self, stmt: Class):
        self.environment.define(stmt.name.lexeme, None)
        methods = {}

        for method in stmt.methods:
            function = LoxFunction(
                method,
                self.environment,
                method.name.lexeme == "init",
            )
            methods[method.name.lexeme] = function

        class_ = LoxClass(stmt.name.lexeme, methods)
        self.environment.assign(stmt.name, class_)

    def visit_expression_stmt(self, stmt: Stmt) -> None:
        evaluated_expr = self.evaluate(stmt.expression)

        if self.is_repl:
            print(self.stringify(evaluated_expr))
        return None

    def visit_function_stmt(self, stmt: Function):
        function: LoxFunction = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, function)
        return None

    def visit_if_stmt(self, stmt: If) -> None:
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_print_stmt(self, stmt: Stmt) -> None:
        value: object = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visit_return_stmt(self, stmt: Return) -> None:
        value: object | None = None

        if stmt.value is not None:
            value = self.evaluate(stmt.value)

        raise LoxReturnException(value)

    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value

    def visit_logical_expr(self, expr: Logical) -> object:
        left: object = self.evaluate(expr.left)

        if expr.operator.token_type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left

        return self.evaluate(expr.right)

    def visit_set_expr(self, expr: Set):
        obj: object = self.evaluate(expr.object)

        if not isinstance(obj, LoxInstance):
            raise LoxRuntimeError(expr.name, "Only instances have fields.")

        value: object = self.evaluate(expr.value)
        obj.set_property(expr.name, value)
        return value

    def visit_this_expr(self, expr: This):
        return self.lookup_variable(expr.keyword, expr)

    def visit_grouping_expr(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def visit_assign_expr(self, expr: Assign):
        value: object = self.evaluate(expr.value)

        distance = self._locals.get(expr)

        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self._globals.assign(expr.name, value)

        return value

    def visit_binary_expr(self, expr: Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.MINUS:
                self.check_number_operands(expr.operator, right, right)
                return left - right
            case TokenType.SLASH:
                self.check_number_operands(expr.operator, left, right)
                return left / right
            case TokenType.STAR:
                self.check_number_operands(expr.operator, left, right)
                return left * right
            case TokenType.PLUS:
                self.check_number_string_operands(expr.operator, left, right)
                return left + right
            case TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return left >= right
            case TokenType.LESS:
                self.check_number_operands(expr.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return left <= right
            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)

    def visit_call_expr(self, expr: Call):
        callee: object = self.evaluate(expr.callee)
        args: list[object] = []

        for arg in expr.arguments:
            args.append(self.evaluate(arg))

        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")

        function: LoxCallable = callee

        if len(args) != function.arity:
            raise LoxRuntimeError(
                expr.paren, f"Expected {function.arity} arguments, but got {len(args)}."
            )

        return function.call(self, args)

    def visit_get_expr(self, expr: Get):
        obj: object = self.evaluate(expr.object)

        if isinstance(obj, LoxInstance):
            return obj.get_property(expr.name)

        raise LoxRuntimeError(expr.name, "Only instances have properties.")

    def visit_unary_expr(self, expr: Unary):
        right: object = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -1 * right
            case TokenType.BANG:
                return not self.is_truthy(right)

    def visit_variable_expr(self, expr: Variable):
        return self.lookup_variable(expr.name, expr)

    def lookup_variable(self, name: Token, expr: Expr):
        distance = self._locals.get(expr)

        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self._globals.get(name)

    def visit_var_stmt(self, stmt: Var) -> None:
        value: object = None

        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)

    def visit_while_stmt(self, stmt: While) -> None:
        try:
            while self.is_truthy(self.evaluate(stmt.condition)):
                try:
                    self.execute(stmt.body)
                except Exception:
                    pass
        except Interpreter.LoxBreakException:
            return

    def visit_break_stmt(self, stmt: Break) -> None:
        raise Interpreter.LoxBreakException()

    def evaluate(self, expr: Expr) -> object:
        return expr.accept(self)

    def is_equal(self, left: object, right: object) -> bool:
        return left == right

    def is_truthy(self, value: object) -> bool:
        if value is None:
            return False

        if isinstance(value, bool):
            return value

        return True

    def check_number_operand(self, operator: Token, operand: object):
        if isinstance(operand, float):
            return

        raise LoxRuntimeError(operator, "Operand must be a number.")

    def check_number_operands(
        self,
        operator: Token,
        left: object,
        right: object,
    ):
        if isinstance(left, float) and isinstance(right, float):
            return

        raise LoxRuntimeError(operator, "Operands must be numbers.")

    def check_number_string_operands(
        self,
        operator: Token,
        left: object,
        right: object,
    ):
        if isinstance(left, float) and isinstance(right, float):
            return

        if isinstance(left, str) and isinstance(right, str):
            return

        raise LoxRuntimeError(operator, "Operands must be two numbers or two strings.")

    def stringify(self, value: object):
        if value is None:
            return "nil"

        if isinstance(value, float):
            text: str = str(value)

            if text.endswith(".0"):
                return text[0:-2]

        if isinstance(value, bool):
            return str(value).lower()

        return str(value)
