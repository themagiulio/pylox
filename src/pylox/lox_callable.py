class LoxCallable:
    def call(self, interpreter, args: list[object]) -> None:
        pass

    @property
    def arity(self) -> int:
        return 0
