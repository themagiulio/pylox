from pylox.token import Token
from pylox.token_type import TokenType
from pylox.visitor import Visitor
from pylox.expr import Expr, Assign, Binary, Literal, Grouping, Unary, Variable
from pylox.stmt import Stmt, Block, Var
from pylox.environment import Environment
from pylox.error_handler import ErrorHandler
from pylox.runtime_error import LoxRuntimeError


class Interpreter(Visitor):
    error_handler: ErrorHandler
    environment: Environment = Environment()
    is_repl: bool

    def __init__(self, error_handler: ErrorHandler, is_repl: bool = False):
        self.error_handler = error_handler
        self.is_repl = is_repl

    def interpret(self, stmts: list[Stmt]):
        try:
            for stmt in stmts:
                self.execute(stmt)
        except LoxRuntimeError as err:
            self.error_handler.runtime_error(err)

    def execute(self, stmt: Stmt):
        stmt.accept(self)

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

    def visit_expression_stmt(self, stmt: Stmt) -> None:
        evaluated_expr = self.evaluate(stmt.expression)

        if self.is_repl:
            print(self.stringify(evaluated_expr))
        return None

    def visit_print_stmt(self, stmt: Stmt) -> None:
        value: object = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value

    def visit_grouping_expr(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def visit_assign_expr(self, expr: Assign):
        value: object = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
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

    def visit_unary_expr(self, expr: Unary):
        right: object = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -1 * right
            case TokenType.BANG:
                return not self.is_truthy(right)

    def visit_variable_expr(self, expr: Variable):
        return self.environment.get(expr.name)

    def visit_var_stmt(self, stmt: Var) -> None:
        value: object = None

        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)

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
