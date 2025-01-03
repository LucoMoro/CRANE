from unittest import skipIf

from network.agents.moderator import Moderator
from network.agents.reviewer import Reviewer
from network.communication.message import Message
import json
import os

from network.config import base_path


class Conversation:
    def __init__(self, moderator: Moderator, reviewers: list[Reviewer]):
        self.moderator = moderator
        self.reviewers = reviewers
        self.history = []

        self.iteration_id = "0"
        self.conversation_id = "0"

        self.base_path = base_path
        self.conversation_manager_path = os.path.join(self.base_path, "conversation_id.json")

    def get_conversation_id(self) -> str:
        """
        Retrieves the `conversation_id` from the JSON file.

        This method opens the JSON file in read mode, reads the data,
        and extracts the value of the `conversation_id` key. If the
        key does not exist, it defaults to an empty dictionary.

        Returns:
            str: The value of the `conversation_id` attribute, or an
                 empty dictionary if not found.
        """
        with open(self.conversation_manager_path, "r") as conversation_file:
            conversation_data = json.load(conversation_file)
            self.conversation_id = conversation_data.get("conversation_id", {})
            return self.conversation_id

    def set_conversation_id(self, new_conversation_id: str) -> None:
        """
        Updates the `conversation_id` in the JSON file with a new value.

        This method reads the existing JSON data from the file, updates
        the value of the `conversation_id` key, and then writes the updated
        data back to the file.

        Args:
            new_conversation_id (str): The new value to assign to the
                                       `conversation_id` key.
        """
        with open(self.conversation_manager_path, "r") as read_conversation_file:
            conversation_data = json.load(read_conversation_file)
            conversation_data["conversation_id"] = new_conversation_id

            with open(self.conversation_manager_path, "w") as write_conversation_file:
                json.dump(conversation_data, write_conversation_file, indent=4)

    def increment_conversation_id(self):
        int_conversation_id = int(self.conversation_id)
        int_conversation_id = int_conversation_id + 1
        self.set_conversation_id(str(int_conversation_id))

    def reset_conversation(self):
        self.set_conversation_id("0")

    def ensure_conversation_path(self) -> str:
        """
        Ensures the existence of a directory path for the current conversation.
        If the directory does not exist, it is created.

        Returns:
            str: The full path to the current conversation's directory.
        """
        current_conversation = f"conversation_{self.get_conversation_id()}"
        full_conversation_path = os.path.join(self.base_path, current_conversation)
        if not os.path.exists(full_conversation_path):
            os.makedirs(full_conversation_path)
        return full_conversation_path

    def get_iteration_id(self) -> str:
        """
        Retrieves the `iteration_id` from the JSON file.

        This method opens the JSON file in read mode, reads the data,
        and extracts the value of the `iteration_id` key. If the
        key does not exist, it defaults to an empty dictionary.

        Returns:
            str: The value of the `iteration_id` attribute, or an
                 empty dictionary if not found.
        """
        with open(self.conversation_manager_path, "r") as iteration_file:
            iteration_data = json.load(iteration_file)
            self.iteration_id = iteration_data.get("iteration_id", {})
            return self.iteration_id

    def set_iteration_id(self, new_iteration_id: str) -> None:
        """
        Updates the `iteration_id` in the JSON file with a new value.

        This method reads the existing JSON data from the file, updates
        the value of the `iteration_id` key, and then writes the updated
        data back to the file.

        Args:
            new_iteration_id (str): The new value to assign to the
                                       `iteration_id` key.
        """
        with open(self.conversation_manager_path, "r") as read_iteration_file:
            iteration_data = json.load(read_iteration_file)
            iteration_data["iteration_id"] = new_iteration_id

            with open(self.conversation_manager_path, "w") as write_iteration_file:
                json.dump(iteration_data, write_iteration_file, indent=4)

    def increment_iteration_id(self):
        int_iteration_id = int(self.iteration_id)
        int_iteration_id = int_iteration_id + 1
        self.set_iteration_id(str(int_iteration_id))

    def reset_iteration(self):
        self.set_iteration_id("0")

    def ensure_iteration_path(self) -> str:
        """
        Ensures the existence of a directory path for the current iteration within a conversation.
        If the directory does not exist, it is created.

        Returns:
            str: The full path to the current iteration's directory.
        """
        current_iteration = f"conversation_{self.get_conversation_id()}/iteration_{self.get_iteration_id()}"
        full_iteration_path = os.path.join(self.base_path, current_iteration)
        if not os.path.exists(full_iteration_path):
            os.makedirs(full_iteration_path)
        return full_iteration_path

    def save_model_responses(self, messages: list[Message]) -> None:
        """
        Saves a list of model responses as a JSON file in the current iteration's directory.

        Args:
            messages (list[Message]): The list of messages to save, where each message is expected
            to be an instance of the Message class.
        """

        full_path = os.path.join(self.base_path, f"conversation_{self.get_conversation_id()}/iteration_{self.get_iteration_id()}")
        output_file = os.path.join(full_path, "responses.json")
        data = {
            "conversation_id": self.conversation_id,
            "iteration_id": self.iteration_id,
            "responses": messages
        }
        with open(output_file, "w") as output:
            json.dump(data, output, indent=4)

    def set_message(self, message: Message) -> None:
        self.history.append(message)

    def add_message(self, message: Message) -> list[Message]:
        """
        Adds a message to the conversation's history.

        Args:
            message (Message): A response obtained by the model.

        Returns:
            list[Message]: list of messages that compose the conversation.
        """
        self.history.append(message.to_dict())
        return self.history

    def get_history(self) -> list[Message]:
        return self.history

    def get_moderator(self) -> Moderator:
        return self.moderator

    def set_moderator(self, new_moderator: Moderator) -> None:
        self.moderator = new_moderator

    def get_reviewers(self) -> list[Reviewer]:
        return self.reviewers

    def set_reviewers(self, new_reviewers: list[Reviewer]) -> None:
        self.reviewers = new_reviewers

    #todo: change every tmp_mod_response to mod_response when a performing LLM will be used
    def simulate_iteration(self, input_text: str = None) -> None:
        self.moderator.set_full_prompt(self.moderator.get_instructions(), input_text, self.moderator.get_context()) #todo delete here this setup
        mod_response = self.moderator.query_model()
        if mod_response is None:
            print("An error occurred.")
            return None
        first_reviewer = ""

        tmp_mod_response = "reviewer_2" #simulates the variable mod_response, which will only contain the name of the
                                        #model that will need to be asked first.

        for reviewer in self.reviewers:
            if reviewer.get_name() == tmp_mod_response: #this if statement has to be executed only at the start of each iteration
                reviewer_response = reviewer.query_model()
                if reviewer_response is None:
                    print("An error occurred.")
                    return None
                reviewer.increment_iteration_messages()
                message = Message(reviewer.get_name(), reviewer_response)
                self.add_message(message)
                first_reviewer = reviewer.get_name()
                tmp_mod_response = "" #this ensures that once the model has been called the first time, it will lose his priority

        for i in range(1): #todo: change the constant to 2 when a performing LLM will be used
            for reviewer in self.reviewers:
                reviewer.set_full_prompt(reviewer.get_instructions(), self.history)
                if reviewer.get_name() != first_reviewer:
                    if reviewer.get_iteration_messages() < 1: #todo: change the constant to 2 when a performing LLM will be used
                       reviewer_response = reviewer.query_model()
                       if reviewer_response is None:
                           print("An error occurred.")
                           return None
                       reviewer.increment_iteration_messages()
                       message = Message(reviewer.get_name(), reviewer_response)
                       self.add_message(message)
                    first_reviewer = "" #this ensures that once the other models have also responded, the first model will be able to respond too again

        self.ensure_conversation_path()
        self.ensure_iteration_path()
        self.save_model_responses(self.history)
        self.increment_iteration_id()
