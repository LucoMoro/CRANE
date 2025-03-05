import os
import json

from network.agents.agent_base import AgentBase
from network.communication.conversation import Conversation
from network.communication.message import Message
from network.config import base_path
from network.utils.error_logger import ErrorLogger
from network.utils.feedback_exception import FeedbackException
from network.utils.summarization_exception import SummarizationException


class ConversationManager:
    def __init__(self, conversation: Conversation, max_retries: int = None):
        #fundamental setup
        self.conversation = conversation
        self.moderator = self.conversation.get_moderator()
        self.reviewers = self.conversation.get_reviewers()
        self.feedback_agent = self.conversation.get_feedback_agent()

        #handling files
        self.iteration_id = "0"
        self.conversation_id = "0"
        self.base_path = base_path
        self.conversation_manager_path = os.path.join(self.base_path, "conversation_id.json")

        #conversation's settings
        self.stopping_condition = False
        if max_retries is None:
            self.max_retries = 5
        else:
            self.max_retries = max_retries
        self.error_logger = ErrorLogger()


    def get_max_retries(self) -> int:
        return self.max_retries

    def set_max_retries(self, new_max_retries) -> None:
        self.max_retries = new_max_retries

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

    def save_moderator_response(self, message, file_name: str) -> None:
        """
        Saves the response of the moderator as a JSON file in the current iteration's directory.

        Args:
            message: The messages to save. It is expected to be an instance of the Message class.
            file_name (str): the name of the json file in which the response has to be saved
        """
        full_path = os.path.join(self.base_path, f"conversation_{self.get_conversation_id()}/iteration_{self.get_iteration_id()}")
        moderator_file = os.path.join(full_path, f"{file_name}.json")
        data = {
            "conversation_id": self.conversation_id,
            "iteration_id": self.iteration_id,
            "response": [message]
        }
        with open(moderator_file, "w") as output:
            json.dump(data, output, indent=4)

    def save_feedback_agent_response(self, message, file_name: str) -> None:
        full_path = os.path.join(self.base_path, f"conversation_{self.get_conversation_id()}/iteration_{self.get_iteration_id()}")
        feedback_agent_file = os.path.join(full_path, f"{file_name}.json")
        data = {
            "conversation_id": self.get_conversation_id(),
            "iteration_id": self.get_iteration_id(),
            "response": [message]
        }
        with open(feedback_agent_file, "w") as output:
            json.dump(data, output, indent=4)

    def save_errors(self) -> None:
        full_path = os.path.join(self.base_path, f"conversation_{self.conversation_id}/iteration_{self.iteration_id}")
        errors_file = os.path.join(full_path, "errors.txt")

        with open (errors_file, "w") as output:
            output.write(self.error_logger.from_array_to_text(f"iteration n.{self.iteration_id}"))
        self.error_logger.reset_errors()

    def simulate_iteration(self, input_text: str = None) -> None:
        """
        Simulates an iteration of a multi-model review and response process.

        This method orchestrates the interactions between a "moderator" model and a list of "reviewer"
        models. It ensures that all models contribute to the conversation.

        Args:
            input_text (str, optional): Input of the current iteration.

        **Moderator Initialization**:
           - Based on the input, the moderator's prompt is set and then queried.
           - As a response, the moderator determines the first reviewer to be queried in the current iteration.

        **Initial Reviewer Selection**:
           - The first reviewer response is processed and added to the iteration history.

        **Subsequent Review Rounds**:
           - All reviewers, except the initial one, are queried ensuring that each reviewer contributes at most 2 times in each iteration.
           - Reviewer responses are processed and added to the iteration history

        **Finalization**:
           - Validates the conversation's integrity and iteration path.
           - Increments the iteration ID to track progress.
        """

        self.initial_review_selection(input_text)
        self.subsequent_rounds()

        self.save_model_responses(self.conversation.get_history())
        self.increment_iteration_id()
        self.reset_iteration_messages()

    def initial_review_selection(self, input_text):
        for reviewer in self.reviewers:
            print(f"Sending request to {reviewer.get_name()} with data: {reviewer.get_instructions()}")
            for i in range(0, 2):
                reviewer_response = reviewer.query_model()
                if reviewer_response is None:
                    self.error_logger.add_error("An error occurred while communicating with the feedback agent.")
                elif reviewer_response is not None:
                    message = Message(reviewer.get_name(), reviewer_response)
                    self.conversation.add_message(message)

    def subsequent_rounds(self) -> None:
        for i in range(1): #todo: change the constant to 2 when a performing LLM will be used
            for reviewer in self.reviewers:
                reviewer.set_full_prompt(reviewer.get_instructions(), self.conversation.get_history())
                if reviewer.get_iteration_messages() < 1: #todo: change the constant to 2 when a performing LLM will be used
                    reviewer_response = reviewer.query_model()
                    if reviewer_response is None:
                        self.error_logger.add_error(f"An error occurred wile trying to communicate with {reviewer.get_name()}.")
                        self.from_agent_get_errors(reviewer)
                        reviewer_response = "" #the reviewers are non-blocking: if some user do not respond, the conversation will proceed
                    reviewer.increment_iteration_messages()
                    message = Message(reviewer.get_name(), reviewer_response)
                    self.conversation.add_message(message)

    def simulate_conversation(self, input_text: str = None) -> None:
        self.ensure_conversation_path() #ensures that the conversation's folder path exists

        self.ensure_iteration_path() #ensures that the iteration's folder path exists
        self.simulate_iteration(input_text) #simulates the iteration
        self.check_stopping_condition() #checks if the stopping condition is reached
        self.save_errors()

        for i in range (0, 1): #todo change in more rounds
        #while not self.stopping_condition:
            print(f"Entering in the iteration number {self.get_iteration_id()}")
            self.ensure_iteration_path() # ensures that the iteration's folder path exists
            summarized_history = self.summarize_iteration_history() #summarizes the previous iteration's history
            current_input_text = self.fetch_model_feedback(summarized_history) #provides the summarized history as a feedback to the model
            self.simulate_iteration(current_input_text)  # simulates the iteration
            self.check_stopping_condition()  # checks if the stopping condition is reached
            self.save_errors()

        self.increment_conversation_id()
        self.reset_iteration()

    def fetch_model_feedback(self, summarized_history) -> str:
        """
        Fetches feedback from the model based on the agent's instructions and history.

        This method constructs a prompt using the agent's instructions and history.
        If a response is successfully retrieved, it is returned immediately.

        Returns:
            str: The feedback response from the model.
        """
        self.feedback_agent.set_full_prompt(self.feedback_agent.get_instructions(), summarized_history)
        for i in range(0, self.max_retries):
            feedback_response = self.feedback_agent.query_model()
            if feedback_response is None:
                self.error_logger.add_error("An error occurred while communicating with the feedback agent.")
            elif feedback_response is not None:
                feedback_message = Message(self.feedback_agent.get_name(), feedback_response)
                self.save_feedback_agent_response(feedback_message.to_dict(), "change")
                return feedback_response
        self.reset_iteration()
        self.error_logger.add_error(f"The feedback agent failed to provide a valid response after {self.max_retries} attempts.")
        raise FeedbackException(f"The feedback agent failed to provide a valid response after {self.max_retries} attempts.")

    def summarize_iteration_history(self) -> str | None:
        """
        Summarizes the input history using the moderator.

        This method constructs a summarization prompt based on the moderator's summarization prompt
        and the current history. If successful, the history is cleared to make room for the new history,
        and the summarized response is returned.

        Returns:
            str: The summarized response from the moderator model.
                 Returns an empty string if no valid response is obtained.
        """
        summarized_response = ""
        self.moderator.set_full_prompt(self.moderator.get_summarization_prompt(), self.conversation.get_history())
        for i in range(0, self.max_retries):
            summarized_response = self.moderator.query_model()
            if summarized_response is None:
                self.error_logger.add_error(f"Attempt {i}: An error occurred while communicating with the moderator during the summarization of the input.")
            elif summarized_response is not None:
                moderator_message = Message(self.moderator.get_name(), summarized_response)
                self.save_moderator_response(moderator_message.to_dict(), "summary")
                self.conversation.set_history([]) #if the history is correctly summarized, the iteration's history will be deleted leaving space for the new one
                return summarized_response
        self.reset_iteration()
        self.error_logger.add_error(f"The moderator failed to provide a valid response after {self.max_retries} attempts.")
        raise SummarizationException(f"The moderator failed to provide a valid response after {self.max_retries} attempts.")

    def check_stopping_condition(self) -> bool:
        """
        Checks whether the stopping condition for the process has been met.

        Returns:
            bool: returns True if the stopping condition has been met.
        """
        self.stopping_condition = True
        return True

    def reset_iteration_messages(self) -> None:
        for reviewer in self.reviewers:
            reviewer.set_iteration_messages(0)

    def from_agent_get_errors(self, agent: AgentBase) -> None:
        """
        Collects error logs from a given agent and adds them to the central error logger.

        Returns:
            None: This method modifies the internal error logger by adding errors retrieved
                  from the provided agent.

        """
        reviewer_errors = agent.get_error_logger()
        for error in reviewer_errors:
            self.error_logger.add_error(error)