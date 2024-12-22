import json

import requests
from network.config import headers

class AgentBase:
    def __init__(self, file_path):
        try:
            with open(file_path, "r") as agent:
                agent_data = json.load(agent)

            self.api_settings = agent_data.get("api_settings", {})
            self.system_prompt = agent_data.get("system_prompt", {})
            self.utils = agent_data.get("utils", {})
            self.default_provider = self.api_settings.get("default_provider", {})

            if self.default_provider == "openai":
                self.open_ai = self.api_settings.get("openai", {})
                self.model = self.open_ai.get("model", {})
                self.endpoint = self.open_ai.get("endpoint", {})
                self.api_key = self.open_ai.get("api_key", {})
                self.hugging_face = None
            else:
                self.hugging_face = self.api_settings.get("huggingface", {})
                self.model = self.hugging_face.get("model", {})
                self.endpoint = self.hugging_face.get("endpoint", {})
                self.api_key = self.hugging_face.get("api_key", {})
                self.open_ai = None

            self.context = self.system_prompt.get("context", {})
            self.instructions = self.system_prompt.get("instructions", {})

            self.utils = agent_data.get("utils", {})
            self.role = self.utils.get("role", {})
            self.specialization = self.utils.get("specialization", {})
            self.name = self.utils.get("name", {})

        except FileNotFoundError:
            print(f"Error: File {file_path} not found")

        except json.JSONDecodeError:
            print("Error while reading the JSON file")

    def print(self):
        print(self.hugging_face)
        print(self.open_ai)
        print(self.default_provider)
        print(self.context)
        print(self.instructions)
        print(self.utils)

    def query_model(self) -> str | None:
        """
        Sends a question to a model via a POST request and returns the model's response.

        Parameters:
        ----------
        question : str
            The question or input text to send to the Hugging Face model.

        Returns:
        -------
        str or None
            If the request is successful (status code 200), returns the response from the model as a str.
            If the request fails, prints an error message with the status code and error details, and returns None.

        Notes:
        -----
        This function assumes that `api_url` (the endpoint URL of the Hugging Face model) and `headers`
        (the request headers, including any required authorization) are defined elsewhere in the code.
        """
        response = requests.post(self.endpoint, headers=headers, json={"inputs": self.instructions})

        if response.status_code == 200:
            return response.json()[0]["generated_text"]
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None

    def get_context(self) -> str:
        return self.context

    def set_context(self, context: str) -> None:
        self.context = context

    def get_instructions(self) -> str:
        return self.instructions

    def set_instructions(self, instructions: str | dict) -> None:
        self.instructions = instructions

    def get_full_prompt(self) -> str:
        """
        Constructs and returns a prompt string based on the configured provider.

        If the default provider is "openai", the function returns the instructions directly.
        Otherwise, it constructs a prompt string by combining the context and instructions

        Returns:
            str: The formatted prompt string.
        """
        if self.default_provider == "openai":
            return self.instructions
        else:
            result = f"System prompt: {self.context} \n prompt: {self.instructions}"
            return result

    #todo change each tmp_input_text_strings to input_text_strings when a performing LLM will be used
    def set_full_prompt(self, instructions: str, input_text: str, context: str = None) -> None:
        """
        Sets the instructions and optional context for the model in the initial step.

        Changes the context only if a new one is provided.

        Args:
            instructions (str): The main instructions or prompt to set.
            input_text(str): input of the iteration or conversation which has to be provided to the models.
            context(str): Additional argument to pass a specific context (default is None).

        Returns:
          None
        """
        #input_text_strings = [str(item) for item in input_text]
        tmp_input_text_strings = "" #simulated the behaviour of input_text_strings which transforms the dictionary of
                                    #input_texts into strings
        self.set_instructions(instructions + "\n\n" .join(tmp_input_text_strings))
        if context is not None:
            self.set_context(context)

    def get_name(self) -> str:
        return self.name

