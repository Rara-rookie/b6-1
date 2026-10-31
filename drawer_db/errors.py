class DrawerError(Exception):
    def __init__(self, message: str, hint: str | None = None):
        self.message = message
        self.hint = hint
        full_message = message if hint is None else f"{message} (hint: {hint})"
        super().__init__(full_message)
