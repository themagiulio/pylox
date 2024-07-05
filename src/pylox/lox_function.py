from typing import Final

from pylox.environment import Environment
from pylox.lox_callable import LoxCallable
from pylox.lox_exceptions import LoxReturnException
from pylox.stmt import Function


class LoxFunction(LoxCallable):
    declaration: Final[Function]
    closure: Final[Environment]
    is_initializer: Final[bool]

    def __init__(
        self,
        declaration: Function,
        closure: Environment,
        is_initializer: bool,
    ):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(
            self.declaration,
            environment,
            self.is_initializer,
        )

    def call(self, interpreter, args: list[object]):
        environment: Environment = Environment(self.closure)

        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, args[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except LoxReturnException as return_stmt:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_stmt.value

        if self.is_initializer:
            return self.closure.get_at(0, "this")

        return None

    def to_string(self):
        return f"<fn {self.declaration.name.lexeme}>"

    @property
    def arity(self):
        return len(self.declaration.params)
