import json

class Message:
    def __init__(self, sender, content):
        self.sender = sender
        self.content = content


    def to_dict(self) -> dict:
        """
        Converts the message in a dictionary.

        Returns:
            dict: dictionary composed by a sender and a message
        """
        return {
            "sender": self.sender,
            "content": self.content
        }