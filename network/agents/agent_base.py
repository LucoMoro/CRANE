import json

import requests
from network.config import huggingface_headers, openai_headers
import re

from network.utils.error_logger import ErrorLogger


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

            self.error_logger = ErrorLogger()

        except FileNotFoundError:
            self.error_logger.add_error(f"Error: File {file_path} not found")

        except json.JSONDecodeError:
            self.error_logger.add_error("Error while reading the JSON file")

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
                payload, headers = self.prepare_payload()
                response = requests.post(self.endpoint, headers=headers, json=payload, timeout=self.timeout)

                if response.status_code == 200:
                    return self.clear_response(response) #based on the provider, the response will be cleared in order to maintain only the output of the agent
                else:
                    self.handle_response_error(response)

            except requests.exceptions.Timeout:
                self.error_logger.add_error(f"Request timed out. Please {self.name} try again later.")
                return None
            except requests.exceptions.ConnectionError:
                self.error_logger.add_error(f"Connection error occurred. {self.name} check your network connection.")
                return None
            except requests.exceptions.RequestException as e:
                self.error_logger.add_error(f"An error occurred({self.name}): {e}")
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

    def get_instructions_from_response(self, response) -> str | None:
        """
        Extracts the generated instructions from the model's response based on the default provider.

        This method handles the response differently depending on whether the provider is OpenAI or Hugging Face:
        - For OpenAI: Assumes the response contains the generated output in a specific format and returns the generated text.
        - For Hugging Face: Uses a regular expression to extract the instructions from the generated text, specifically looking for content after the "Instructions:" label.

        Args:
            response: The HTTP response object from the API call. It is expected to contain a JSON payload with the generated output.

        Returns:
            str | None: The extracted instructions as a string, or `None` if no instructions could be extracted or the response format is invalid.
        """
        if self.default_provider == "openai":
            # todo: check which pattern is produced by the openai response and try to maintain only the output while excluding the input taken by the LLM
            return response.json()[0]["generated_text"]
        elif self.default_provider == "huggingface":
            pattern = r"Instructions: \s*(.*)"
            match = re.search(pattern, response.json()[0]["generated_text"], re.DOTALL)
            if match:
                return match.group(1)
            else:
                return None

    def delete_prompt_from_response(self, instructions) -> str:
        """
        Removes the input prompt from the generated response provided by the LLM.

        This function processes the response text returned by the LLM and removes
        any portion of the response that matches the original input instructions.
        The behavior differs based on the default provider:

        Args:
            instructions (str): The full response text returned by the LLM,
            which may include both the input prompt and the generated output.

        Returns:
            str | None: The filtered response text with the input prompt removed.
        """
        if self.default_provider == "openai":
            # todo: check which pattern is produced by the openai response and try to maintain only the output while excluding the input taken by the LLM
            return instructions
        elif self.default_provider == "huggingface":
            result = instructions.replace(self.instructions, "")
            return result

    def get_name(self) -> str:
        return self.name

    def get_default_provider(self) -> str:
        return self.default_provider

    def get_error_logger(self) -> list[str]:
        return self.error_logger.get_errors()

    def set_error_logger(self, error_logger: list[str]) -> None:
        self.error_logger.set_errors(error_logger)

    def get_huggingface_payload(self) -> dict:
        """
        Constructs the payload for a Hugging Face API request.

        This method creates a dictionary payload formatted for Hugging Face's
        text generation models. The payload includes the context, user instructions,
        and maximum token limits.

        Returns:
            dict: A dictionary containing the following keys:
                - "inputs" (str): A string combining the context and instructions,
                  formatted as "Context: {self.context}\nInstructions: {self.instructions}".
                - "parameters" (dict): A dictionary containing:
                    - "max_new_tokens" (int): The maximum number of tokens to generate.
        """
        payload = {
            "inputs": f"Context: {self.context}\nInstructions: {self.instructions}",
            "parameters": {
                "max_new_tokens": int(self.max_tokens),  # Add token limit for Hugging Face
            }
        }
        return payload

    def get_openai_payload(self) -> dict:
        """
            Constructs the payload for an OpenAI API request.

            This method creates a dictionary payload formatted for OpenAI's
            chat-based language models (e.g., GPT). The payload includes the
            model name, context, user instructions, and token limits.

            Returns:
                dict: A dictionary containing the following keys:
                    - "model" (str): The name of the OpenAI model to be used.
                    - "messages" (list): A list of dictionaries representing the conversation,
                      with each dictionary containing:
                        - "role" (str): The role in the conversation ("system" or "user").
                        - "content" (str): The corresponding text content (context or instructions).
                    - "max_tokens" (int): The maximum number of tokens to generate.
            """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.context},
                {"role": "user", "content": self.instructions}
            ],
            "max_tokens": int(self.max_tokens),
        }
        return payload

    def prepare_payload(self):
        if self.default_provider == "openai":
            payload = self.get_openai_payload()
            headers = openai_headers
            return payload, headers
        elif self.default_provider == "huggingface":
            payload = self.get_huggingface_payload()
            headers = huggingface_headers
            return payload, headers
        else:
            raise ValueError("Unsupported provider")


    def clear_response(self, response) -> str:
        filtered_response = ""
        if self.default_provider == "openai":
            filtered_response = response.json()["choices"][0]["message"]["content"]
        if self.default_provider == "huggingface":
            # print(f"the response length of {self.name} is:" + str(len(response.json()[0]["generated_text"].split())))
            # print(response.json())
            instructions = self.get_instructions_from_response(response)
            # print(f"true instructions: {self.instructions}")
            # print(f"false instructions: {instructions}")
            filtered_response = self.delete_prompt_from_response(instructions)
            # print(f"filtered result: {filtered_result}")
            # print(f"the filtered_result length of {self.name} is:" + str(len(filtered_result.split())))
        return filtered_response

    def handle_response_error(self, response) -> None:
        if response.status_code == 503:
            self.error_logger.add_error(f"Service unavailable ({self.name}): Retrying in {self.wait_time} seconds...")
        elif response.status_code == 400:
            self.error_logger.add_error(f"Bad request ({self.name}): The server could not understand the request.")
        elif response.status_code == 401:
            self.error_logger.add_error(f"Unauthorized ({self.name}): Check your API key or authentication method.")
        elif response.status_code == 403:
            self.error_logger.add_error(f"Forbidden ({self.name}): You do not have permission to access this resource.")
        elif response.status_code == 404:
            self.error_logger.add_error(f"Not found ({self.name}): The request resource could not be found.")
        else:
            self.error_logger.add_error(f"Error {response.status_code}({self.name}): {response.text}")
        return None