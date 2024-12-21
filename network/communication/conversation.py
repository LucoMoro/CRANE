from network.communication.message import Message
import json
import os

class Conversation:
    def __init__(self, moderator, reviewers):
        self.moderator = moderator
        self.reviewers = reviewers
        self.history = []
        self.iteration_id = ""
        self.conversation_id = ""

    def set_message(self, message: Message) -> None:
        self.history.append(message)

    def get_conversation_id(self) -> str:
        """
        Reads and returns the current conversation ID from the conversation_id file.

        Returns:
            str: The conversation ID as a string.
        """
        with open("../conversations/conversation_id", "r") as conversation_file:
            self.conversation_id = conversation_file.read().strip()
            return self.conversation_id

    def set_conversation_id(self, conversation_count: str, file_path: str) -> None:
        """
        Overwrites the ID of the current conversation from the conversation_id file

        Args:
            conversation_count (str): The content to write into the file.
            file_path (str): Path of the current conversation_id file.
        """
        with open(file_path, "w") as conversation_file:
            conversation_file.write(conversation_count)

    def get_iteration_id(self, file_path: str) -> str:
        """
        Reads and returns the current iteration ID from the iteration_id file.

        Args:
            file_path (str): Path of the current iteration_id file.

        Returns:
            str: The iteration ID as a string.
        """
        with open(file_path, "r") as iteration_file:
            self.iteration_id = iteration_file.read().strip()
            return self.iteration_id

    def set_iteration_id(self, iteration_count: str, file_path: str) -> None:
        """
        Overwrites the ID of the current iteration from the iteration_id file

        Args:
            iteration_count (str): The content to write into the file.
            file_path (str): Path of the current iteration_id file.
        """
        with open(file_path, "w") as iteration_file:
            iteration_file.write(iteration_count)

