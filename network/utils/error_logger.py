
class ErrorLogger:
    def __init__(self):
        self.errors = []

    def get_errors(self) -> list[str]:
        return self.errors

    def set_errors(self, errors: list[str]) -> None:
        self.errors = errors

    def add_error(self, new_error: str) -> None:
        self.errors.append(new_error)

    def from_array_to_text(self, context_text) -> str:
        """
            Converts a list of error messages into a formatted string, appending them to a given context.

            Args:
                context_text (str): A string that provides context for the error messages.
                                    This is prepended to the formatted error log.

            Returns:
                str: A single string that includes the context text followed by all the
                     error messages from the `self.errors` list.
            """
        errors = ""

        for item in self.errors:
            errors = errors + item + '\n'

        text = f"""{context_text}:\n{errors}"""
        return text

    def reset_errors(self) -> None:
        self.errors = []