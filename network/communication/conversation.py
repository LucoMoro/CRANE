from unittest import skipIf

from network.communication.message import Message
import json
import os

class Conversation:
    def __init__(self, moderator, reviewers):
        self.moderator = moderator
        self.reviewers = reviewers
        self.history = []
        self.iteration_id = "0"
        self.conversation_id = "0"

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

        Returns:
            str: The full path to the conversation iteration directory.
        """
        conversation_path = f"../conversations/conversation_{self.conversation_id}/iteration_{self.iteration_id}"
        existing_path = os.path.exists(conversation_path)
        if not existing_path:
            os.makedirs(conversation_path)
        return conversation_path

    def save_model_responses(self, messages: list[Message] ) -> None:
        """
        Saves the messages for a specific conversation and iteration.

        This function creates a JSON file containing the models' responses,
        along with metadata about the conversation and iteration.

        Args:
            messages (list[Message]): A list of responses from the model.

        Returns:
            None
        """
        responses_iteration_path = f"../conversations/conversation_{self.conversation_id}/iteration_{self.iteration_id}"
        output_file = os.path.join(responses_iteration_path, "responses.json")

        data = {
            "conversation_id": self.conversation_id,
            "iteration_id": self.iteration_id,
            "responses": messages
        }

        with open(output_file, "w") as output:
            json.dump(data, output, indent=4)


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

    #todo: change every tmp_mod_response to mod_response when a performing LLM will be used
    def simulate_iteration(self, input_text: str = None) -> None:
        self.moderator.set_full_prompt(self.moderator.get_instructions(), input_text, self.moderator.get_context())
        mod_response = self.moderator.query_model()
        first_reviewer = ""

        tmp_mod_response = "reviewer_3" #simulates the variable mod_response, which will only contain the name of the
                                        #model that will need to be asked first.

        for reviewer in self.reviewers:
            if reviewer.get_name() == tmp_mod_response: #this if statement has to be executed only at the start of each iteration
                reviewer_response =  reviewer.query_model()
                reviewer.increment_iteration_messages()
                message = Message(reviewer.get_name(), reviewer_response)
                self.add_message(message)
                first_reviewer = reviewer.get_name()
                tmp_mod_response = "" #this ensures that once the model has been called the first time, it will lose his priority

        for i in range(1): #it should be 2
            for reviewer in self.reviewers:
                reviewer.set_full_prompt(reviewer.get_instructions(), self.history)
                if reviewer.get_name() != first_reviewer:
                    if reviewer.get_iteration_messages() < 1: #todo: change the constant to 2 when a performing LLM will be used
                       reviewer_response =  reviewer.query_model()
                       reviewer.increment_iteration_messages()
                       message = Message(reviewer.get_name(), reviewer_response)
                       self.add_message(message)
                    first_reviewer = "" #this ensures that once the other models have also responded,
                                        # the first model will be able to respond too again

        self.ensure_conversation_path()
        self.save_model_responses(self.history)
        iteration_id = int(self.iteration_id)
        iteration_id += 1
        self.set_iteration_id(str(iteration_id), f"../conversations/conversation_{self.conversation_id}/iteration_id")