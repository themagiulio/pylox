from typing import Final

from pylox.lox_callable import LoxCallable
from pylox.lox_instance import LoxInstance


class LoxClass(LoxCallable):
    name: Final[str]

    def __init__(self, name: str):
        self.name = name

    def call(self, interpreter, args: list[object]):
        instance: LoxInstance = LoxInstance(self)
        return instance

    @property
    def arity(self) -> int:
        return 0

    def __str__(self):
        return self.name
