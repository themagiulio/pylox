from typing import Final

from pylox.lox_callable import LoxCallable
from pylox.lox_function import LoxFunction
from pylox.lox_instance import LoxInstance


class LoxClass(LoxCallable):
    name: Final[str]
    methods: Final[dict[str, LoxFunction]]

    def __init__(self, name: str, superclass, methods: dict[str, LoxFunction]):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def call(self, interpreter, args: list[object]):
        instance: LoxInstance = LoxInstance(self)
        initializer: LoxFunction = self.find_method("init")

        if initializer is not None:
            initializer.bind(instance).call(interpreter, args)

        return instance

    def find_method(self, name: str):
        if name in self.methods:
            return self.methods[name]

        if self.superclass is not None:
            return self.superclass.find_method(name)

    @property
    def arity(self) -> int:
        initializer: LoxFunction = self.find_method("init")

        if initializer is None:
            return 0

        return initializer.arity

    def __str__(self):
        return self.name
