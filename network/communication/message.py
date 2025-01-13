import json
from lib2to3.fixes.fix_input import context
from operator import truediv

import re

class Message:
    def __init__(self, sender: str, content):
        self.sender = sender
        self.content = content
        self.response_to = ""
        self.response_to_pattern = "in response to: "

    def contains_response_to(self) -> bool:
        """
        Checks if the message is in response to a specific agent

        Returns:
            bool: True if message is in response to a specific agent,
                  False otherwise
        """
        lower_content = self.content.lower()
        if self.response_to_pattern in lower_content:
            return True
        else:
            return False

    def extract_response_to_pattern(self) -> None:
        """
        Extracts the name of the receiver agent to from the content.

        This method searches for a pattern used for responding to a specific agent.
        If a match is found, it assigns the extracted name to `self.response_to`.

        Returns:
             None
        """
        pattern = rf"{self.response_to_pattern}(\w+)"
        lower_content = self.content.lower() #needed to momentarily lower the agent's output
        match = re.search(pattern, lower_content)
        if match:
            self.content = self.content.replace(self.response_to_pattern+""+match.group(1), "") #allows to remove the pattern "in response to: " once is recognized the first time
            self.response_to = match.group(1)
        else:
            self.response_to = ""

    def to_dict(self) -> dict:
        """
        Converts the message in a dictionary.

        Returns:
            result(dict): dictionary composed by a sender a message and an optional field
                          which indicates if the message is in response to a specific agent
        """
        if self.contains_response_to():
            self.extract_response_to_pattern()
            result = {
                "sender": self.sender,
                "content": self.content,
                "in response to": self.response_to
            }
        else:
            result = {
                "sender": self.sender,
                "content": self.content,
            }
        return result