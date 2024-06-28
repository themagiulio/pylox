from pylox.token import Token
from pylox.runtime_error import LoxRuntimeError


class Environment:
    values: dict[str, object] = {}

    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def get(self, name: Token) -> object:
        if name.lexeme in self.values:
            return self.values.get(name.lexeme)

        raise LoxRuntimeError(name, message=f"Undefined variable '{name.lexeme}'.")
