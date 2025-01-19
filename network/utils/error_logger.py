
class ErrorLogger:
    def __init__(self):
        self.errors = []

    def get_errors(self) -> list[str]:
        return self.errors

    def set_errors(self, errors: list[str]) -> None:
        self.errors = errors

    def add_error(self, new_error: str) -> None:
        self.errors.append(new_error)