import json

import requests
from network.config import headers

import re

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
                self.max_tokens = self.open_ai.get("max_tokens", {})
                self.hugging_face = None
            else:
                self.hugging_face = self.api_settings.get("huggingface", {})
                self.model = self.hugging_face.get("model", {})
                self.endpoint = self.hugging_face.get("endpoint", {})
                self.api_key = self.hugging_face.get("api_key", {})
                self.max_tokens = self.hugging_face.get("max_new_tokens", {})
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

        self.request_retries = 2
        self.wait_time = 2
        self.timeout = 10

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
        self.request_retries : int
            Number of times the function will try to call the LLM api before returning an error

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
        for i in range(0, self.request_retries):
            try:
                if self.default_provider == "openai":
                    # OpenAI requires a structured 'messages' format
                    payload = {
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": self.context},
                            {"role": "user", "content": self.instructions}
                        ],
                        "max_tokens": int(self.max_tokens),
                    }
                elif self.default_provider == "huggingface":
                    # Hugging Face uses a single 'inputs' string
                    payload = {
                        "inputs": f"Context: {self.context}\nInstructions: {self.instructions}",
                        "parameters": {
                            "max_new_tokens": int(self.max_tokens),  # Add token limit for Hugging Face
                        }
                    }
                else:
                    raise ValueError("Unsupported provider")

                # Send the request
                response = requests.post(self.endpoint, headers=headers, json=payload, timeout=self.timeout)

                if response.status_code == 200: #based on the provider, the response will be cleared in order to maintain only the output of the agent
                    if self.default_provider == "openai":
                        #todo: check which pattern is produced by the openai response and try to maintain only the output while excluding the input taken by the LLM
                        return response.json()[0]["generated_text"]
                    elif self.default_provider == "huggingface":
                        pattern = r"Instructions: \s*(.*)"
                        match = re.search(pattern, response.json()[0]["generated_text"], re.DOTALL)
                        if match:
                            return match.group(1)
                        else:
                            return None
                elif response.status_code == 503:
                    print(f"Service unavailable. Retrying in {self.wait_time} seconds...")
                elif response.status_code == 400:
                    print("Bad request: The server could not understand the request.")
                elif response.status_code == 401:
                    print("Unauthorized: Check your API key or authentication method.")
                elif response.status_code == 403:
                    print("Forbidden: You do not have permission to access this resource.")
                elif response.status_code == 404:
                    print("Not found: The request resource could not be found.")
                else:
                    print(f"Error {response.status_code}: {response.text}")
                    return None
            except requests.exceptions.Timeout:
                print("Request timed out. Please try again later.")
                return None
            except requests.exceptions.ConnectionError:
                print("Connection error occurred. Check your network connection.")
                return None
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                return None

    def get_context(self) -> str:
        return self.context

    def set_context(self, context: str) -> None:
        self.context = context

    def get_instructions(self) -> str:
        return self.instructions

    def set_instructions(self, instructions: str | dict) -> None:
        self.instructions = instructions

    def get_request_retries(self) -> int:
        return self.request_retries

    def set_request_retries(self, new_request_retries : int) -> None:
        self.request_retries = new_request_retries

    def get_wait_time(self) -> int:
        return self.wait_time

    def set_wait_time(self, new_wait_time : int) -> None:
        self.wait_time = new_wait_time

    def get_timeout(self) -> int:
        return self.timeout

    def set_timeout(self, new_timeout) -> None:
        self.timeout = new_timeout

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

    def set_full_prompt(self, instructions: str, input_text, context: str = None) -> None:
        """
        Sets the instructions and optional context for the model in the initial step.

        Changes the context only if a new one is provided.

        Args:
            instructions (str): The prompt of the model.
            input_text(str): The input of the iteration or conversation which has to be provided to the models.
            context(str): Additional argument to pass a specific context (default is None).

        Returns:
          None
        """
        input_text_strings = [str(item) for item in input_text]
        self.set_instructions(instructions + "\n\n" .join(input_text_strings)) #needed in order to correctly query the model
        if context is not None:
            self.set_context(context)

    def get_name(self) -> str:
        return self.name

