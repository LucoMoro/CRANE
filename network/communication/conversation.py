from unittest import skipIf

from network.communication.message import Message
import json
import os

from network.config import base_path


class Conversation:
    def __init__(self, moderator, reviewers):
        self.moderator = moderator
        self.reviewers = reviewers
        self.history = []

        self.iteration_id = "0"
        self.conversation_id = "0"

        self.base_path = base_path

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
        with open(self.base_path, "r") as conversation_file:
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
        with open(self.base_path, "r") as read_conversation_file:
            conversation_data = json.load(read_conversation_file)
            conversation_data["conversation_id"] = new_conversation_id

            with open(self.base_path, "w") as write_conversation_file:
                json.dump(conversation_data, write_conversation_file, indent=4)


    def get_iteration_id(self) -> str:
        with open(self.base_path, "r") as iteration_file:
            iteration_data = json.load(iteration_file)
            self.iteration_id = iteration_data.get("iteration_id", {})
            return self.iteration_id

    def set_iteration_id(self, new_iteration_id: str) -> None:
        with open(self.base_path, "r") as read_iteration_file:
            iteration_data = json.load(read_iteration_file)
            iteration_data["iteration_id"] = new_iteration_id

            with open(self.base_path, "w") as write_iteration_file:
                json.dump(iteration_data, write_iteration_file, indent=4 )

    def ensure_conversation_path(self) -> str:
        """
        Ensures that a directory for the given conversation iteration exists.

        If the directory does not exist, it creates the directory at the specified
        path. The path is constructed using the base conversations_path and the
        iteration_id.

        Returns:
            str: The full path to the conversation iteration directory.
        """
        conversation_path = f"../../conversations/conversation_{self.conversation_id}/iteration_{self.iteration_id}"
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
        responses_iteration_path = f"../../conversations/conversation_{self.conversation_id}/iteration_{self.iteration_id}"
        output_file = os.path.join(responses_iteration_path, "responses.json")

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

    #todo: change every tmp_mod_response to mod_response when a performing LLM will be used
    def simulate_iteration(self, input_text: str = None) -> None:
        self.moderator.set_full_prompt(self.moderator.get_instructions(), input_text, self.moderator.get_context())
        mod_response = self.moderator.query_model()
        first_reviewer = ""

        tmp_mod_response = "reviewer_2" #simulates the variable mod_response, which will only contain the name of the
                                        #model that will need to be asked first.

        for reviewer in self.reviewers:
            if reviewer.get_name() == tmp_mod_response: #this if statement has to be executed only at the start of each iteration
                reviewer_response =  reviewer.query_model()
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
                       reviewer_response =  reviewer.query_model()
                       reviewer.increment_iteration_messages()
                       message = Message(reviewer.get_name(), reviewer_response)
                       self.add_message(message)
                    first_reviewer = "" #this ensures that once the other models have also responded,
                                        # the first model will be able to respond too again
        print(self.history)
        #self.ensure_conversation_path()
        #self.save_model_responses(self.history)
        #iteration_id = int(self.iteration_id)
        #iteration_id += 1
        #self.set_iteration_id(str(iteration_id), f"../conversations/conversation_{self.conversation_id}/iteration_id")