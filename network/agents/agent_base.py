import json

import os

import requests
from network.config import headers

class AgentBase:
    def __init__(self, file_path):
        with open(file_path, "r") as agent:
            agent_data = json.load(agent)

        self.api_settings = agent_data.get("api_settings", {})
        self.system_prompt = agent_data.get("system_prompt", {})
        self.utils = agent_data.get("utils", {})

        self.open_ai = self.api_settings.get("openai", {})
        self.hugging_face = self.api_settings.get("huggingface", {})
        self.default_provider = self.api_settings.get("default_provider", {})

        self.prompt_context = self.system_prompt.get("context", {})
        self.prompt_instructions = self.system_prompt.get("instructions", {})

        self.endpoint = self.hugging_face.get("endpoint", {})


    def print(self):
        print(self.hugging_face)
        print(self.open_ai)
        print(self.default_provider)
        print(self.prompt_context)
        print(self.prompt_instructions)

    def query_model(self):
        """
        Sends a question to a model via a POST request and returns the model's response.

        Parameters:
        ----------
        question : str
            The question or input text to send to the Hugging Face model.

        Returns:
        -------
        dict or None
            If the request is successful (status code 200), returns the response from the model as a dictionary.
            If the request fails, prints an error message with the status code and error details, and returns None.

        Notes:
        -----
        This function assumes that `api_url` (the endpoint URL of the Hugging Face model) and `headers`
        (the request headers, including any required authorization) are defined elsewhere in the code.
        """
        response = requests.post(self.endpoint, headers=headers, json={"inputs": self.prompt_instructions})

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Errore {response.status_code}: {response.text}")
            return None
