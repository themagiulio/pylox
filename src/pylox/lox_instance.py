class LoxInstance:
    def __init__(self, class_):
        self._class = class_

    def __str__(self):
        return f"{self._class.name} instance"
