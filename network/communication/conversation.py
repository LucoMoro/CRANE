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

    @staticmethod
    def set_conversation_id(conversation_count: str, file_path: str) -> None:
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

    @staticmethod
    def set_iteration_id(iteration_count: str, file_path: str) -> None:
        """
        Overwrites the ID of the current iteration from the iteration_id file

        Args:
            iteration_count (str): The content to write into the file.
            file_path (str): Path of the current iteration_id file.
        """
        with open(file_path, "w") as iteration_file:
            iteration_file.write(iteration_count)

    def ensure_conversation_path(self) -> str:
        """
        Ensures that a directory for the given conversation iteration exists.

        If the directory does not exist, it creates the directory at the specified
        path. The path is constructed using the base conversations_path and the
        iteration_id.

        Args:
            conversations_path (str): The base path for all conversations.

        Returns:
            str: The full path to the conversation iteration directory.
        """
        conversation_path = f"../conversations/conversation_{self.conversation_id}/iteration_{self.iteration_id}"
        existing_path = os.path.exists(conversation_path)
        if not existing_path:
            os.makedirs(conversation_path)
        return conversation_path

    #todo modify this method
    def save_model_responses(self, model_responses) -> None:
        """
        Saves the model responses for a specific conversation and iteration.

        This function creates a JSON file containing the model's responses,
        along with metadata about the conversation and iteration.

        Args:
            model_responses (list): A list of responses from the model.

        Returns:
            None
        """
        responses_iteration_path = f"../conversations/conversation_{self.conversation_id}/iteration_{self.iteration_id}"
        output_file = os.path.join(responses_iteration_path, "responses.json")

        data = {
            "conversation_id": self.conversation_id,
            "iteration_id": self.iteration_id,
            "responses": model_responses
        }

        with open(output_file, "w") as output:
            json.dump(data, output, indent=4)