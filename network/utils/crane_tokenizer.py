import tiktoken

class CraneTokenizer:
    def __init__(self, model):
        self.input_tokens = 0
        self.output_tokens = 0
        self.encoding = tiktoken.encoding_for_model(model)

    def get_input_tokens(self) -> int:
        return self.input_tokens

    def set_input_tokens(self, input_tokens: int) -> None:
        self.input_tokens = input_tokens

    def get_output_tokens(self) -> int:
        return self.output_tokens

    def set_output_tokens(self, output_tokens: int) -> None:
        self.output_tokens = output_tokens

    def add_to_input_tokens(self, input_tokens: int) -> None:
        self.input_tokens = self.input_tokens + input_tokens

    def add_to_output_tokens(self, output_tokens: int) -> None:
        self.output_tokens = self.output_tokens + output_tokens

    def calculate_tokens_from_string(self, string: str) -> int:
        tokens = self.encoding.encode(string)
        return len(tokens)