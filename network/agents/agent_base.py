import json
import os
from platform import system


class AgentBase:
    def __init__(self, file_path):
        with open(file_path, "r") as agent:
            agent_data = json.load(agent)

        api_settings = agent_data.get("api_settings", {})

        self.open_ai = api_settings.get("openai", {})
        self.hugging_face = api_settings.get("huggingface", {})
        self.default_provider = api_settings.get("default_provider", {})

        system_prompt = agent_data.get("system_prompt", {})

        self.prompt_context = system_prompt.get("context", {})
        self.prompt_instructions = system_prompt.get("instructions", {})


    def print(self):
        print(self.hugging_face)
        print(self.open_ai)
        print(self.default_provider)
        print(self.prompt_context)
        print(self.prompt_instructions)
