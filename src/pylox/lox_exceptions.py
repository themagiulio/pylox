from typing import Final


class LoxReturnException(RuntimeError):
    value: Final[object | None]

    def __init__(self, value: object | None):
        super().__init__()
        self.value = value
