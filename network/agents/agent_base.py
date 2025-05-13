import json

import requests
from network.config import huggingface_headers, openai_headers
import re
import tiktoken

from network.utils.crane_tokenizer import CraneTokenizer
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

            self.context = ""
            self.original_context = self.system_prompt.get("context", {})
            self.instructions = self.system_prompt.get("instructions", {})

            self.utils = agent_data.get("utils", {})
            self.role = self.utils.get("role", {})
            self.specialization = self.utils.get("specialization", {})
            self.name = self.utils.get("name", {})
            self.personality = self.utils.get("personality", {})
            self.original_context = f"{self.specialization}\n{self.personality}\n{self.original_context}.\nFurthermore, you have to respond using at most {self.max_tokens} tokens."

            self.input_problem = ""
            self.additional_context = ""
            self.error_logger = ErrorLogger()

        except FileNotFoundError:
            self.error_logger.add_error(f"Error: File {file_path} not found")

        except json.JSONDecodeError:
            self.error_logger.add_error("Error while reading the JSON file")

        self.request_retries = 1
        self.wait_time = 2
        self.timeout = 60

        self.tokenizer = CraneTokenizer("gpt-4o-mini-2024-07-18")

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
                #print(f"Agent: {self.name}\n Payload:<begin>{payload}</end>\n")
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

    def get_original_context(self) -> str:
        return self.original_context

    def set_original_context(self, original_context: str) -> None:
        self.original_context = original_context

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
                - "inputs" (str): A string combining the context and instructions.
                - "parameters" (dict): A dictionary containing:
                    - "max_new_tokens" (int): The maximum number of tokens to generate.
        """
        full_context = (
            f"### System Context\n{self.original_context.strip()}\n\n"
            f"### Conversation History\n{self.additional_context}"
        )

        payload = {
            "inputs": (
                f"{full_context}\n\n"
                f"### Instructions\n{self.instructions}\n### Data provided as input\n{self.input_problem}"
            ),
            "parameters": {
                "max_new_tokens": int(self.max_tokens),  # Add token limit for Hugging Face
            }
        }
        return payload

    def get_openai_payload(self) -> dict:
        """
        Construct the payload for an OpenAI Chat API request.

        This method assembles a payload dictionary compatible with OpenAI's chat-based
        models (e.g., GPT-4). It merges the original system context and the conversational
        history into a unified system message, and includes user instructions for the model
        to respond to.

        Returns:
            dict: A payload dictionary with the following structure:
                - "model" (str): The name of the OpenAI model to use.
                - "messages" (list of dict): A list containing:
                    - {"role": "system", "content": str}: The combined system context and conversation history.
                    - {"role": "user", "content": str}: The user's current instructions or prompt.
                - "max_tokens" (int): The maximum number of tokens allowed in the generated response.
        """
        if self.additional_context == "":
            full_context = (
                f"### System Instructions\n{self.original_context.strip()}\n\n"
                f"### Conversation History\nThere is not yet a conversation history to retrieve."
            )
        else:
            full_context = (
                f"### System Instructions\n{self.original_context.strip()}\n\n"
                f"### Conversation History\n{self.additional_context}"
            )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": full_context},  # Combined context
                {"role": "user", "content": f"### Instructions\n{self.instructions}\n### Data provided as input\n{self.input_problem}"}
            ],
            "max_tokens": int(self.max_tokens),
        }

        #for m in payload["messages"]:
            #tokens = self.tokenizer.calculate_tokens_from_string(m["content"])
            #print(f"Agent {self.name} tokens {tokens}")
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
            #output_tokens = response.json()["usage"]["completion_tokens"]
            #print(f"Agent: {self.name} output tokens {output_tokens}")
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

    def get_input_problem(self):
        return self.input_problem

    def set_input_problem(self, input_problem):
        self.input_problem = input_problem

    def get_additional_context(self):
        return self.additional_context

    def set_additional_context(self, additional_context):
        self.additional_context = additional_context