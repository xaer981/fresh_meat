class ValidationError(Exception):
    def __init__(self, message) -> None:
        super().__init__()
        self.message = message
