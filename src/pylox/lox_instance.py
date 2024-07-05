from pylox.token import Token
from pylox.runtime_error import LoxRuntimeError


class LoxInstance:
    def __init__(self, class_):
        self._class = class_
        self._fields = {}

    def get_property(self, name: Token):
        if name.lexeme in self._fields:
            return self._fields[name.lexeme]

        method = self._class.find_method(name.lexeme)

        if method is not None:
            return method.bind(self)

        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set_property(self, name: Token, value: object):
        self._fields[name.lexeme] = value

    def __str__(self):
        return f"{self._class.name} instance"
