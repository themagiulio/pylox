from typing import Final

from pylox.environment import Environment
from pylox.lox_callable import LoxCallable
from pylox.lox_exceptions import LoxReturnException
from pylox.stmt import Function


class LoxFunction(LoxCallable):
    declaration: Final[Function]
    closure: Final[Environment]

    def __init__(self, declaration: Function, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, args: list[object]):
        environment: Environment = Environment(self.closure)

        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, args[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except LoxReturnException as return_stmt:
            return return_stmt.value
        return None

    def to_string(self):
        return f"<fn {self.declaration.name.lexeme}>"

    @property
    def arity(self):
        return len(self.declaration.params)
