from typing import Final

from pylox.token import Token
from pylox.runtime_error import LoxRuntimeError


class Environment:
    enclosing: Final
    values: dict[str, object]

    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign_at(self, distance: int, name: Token, value: object):
        self.ancestor(distance).values[name.lexeme] = value

    def get(self, name: Token) -> object:
        # Look for variable in current environment
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        # Look for variable in enclosing environment
        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise LoxRuntimeError(name, message=f"Undefined variable '{name.lexeme}'.")

    def get_at(self, distance: int, name: str):
        return self.ancestor(distance).values.get(name)

    def ancestor(self, distance: int):
        environment = self

        for i in range(0, distance):
            environment = environment.enclosing

        return environment
