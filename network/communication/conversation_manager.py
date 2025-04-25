import os
import json

from network.agents.agent_base import AgentBase
from network.communication.conversation import Conversation
from network.communication.message import Message
from network.config import base_path
from network.utils.error_logger import ErrorLogger
from network.utils.feedback_exception import FeedbackException
from network.utils.retrieval_rag_exception import RetrievalRAGException
from network.utils.save_rag_exception import SaveRAGException
from network.utils.summarization_exception import SummarizationException
from network.communication.conversational_rag import ConversationalRAG


class ConversationManager:
    def __init__(self, conversation: Conversation, max_retries: int = None, messages_per_iteration: int = None):
        #fundamental setup
        self.conversation = conversation
        self.moderator = self.conversation.get_moderator()
        self.reviewers = self.conversation.get_reviewers()
        self.feedback_agent = self.conversation.get_feedback_agent()
        self.conversational_rag = ConversationalRAG("https://crane-0nuuost.svc.aped-4627-b74a.pinecone.io")

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

        if messages_per_iteration is None:
            self.messages_per_iteration = 1 #todo: change the constant to 2 when a performing LLM will be used
        else:
            self.messages_per_iteration = messages_per_iteration

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
        """
        Saves the response of the feedback_agent as a JSON file in the current iteration's directory.

        Args:
            message: The messages to save. It is expected to be an instance of the Message class.
            file_name (str): the name of the json file in which the response has to be saved
        """
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
        Simulates a single iteration of the conversation process.

        This method runs the initial review selection using the provided input text,
        then proceeds through a predefined number of message rounds (determined by
        `self.messages_per_iteration`). After completing all rounds, it saves the
        generated model responses, increments the iteration ID, and resets the messages
        for the next iteration.

        Args:
            input_text (str, optional): The input text to initiate the conversation.
            If None, the method uses a default or pre-existing input.

        Returns:
            None
        """

        self.initial_review_selection(input_text)
        for i in range(0, self.messages_per_iteration):
            self.subsequent_rounds(input_text)

        self.save_model_responses(self.conversation.get_history())
        self.increment_iteration_id()
        self.reset_iteration_messages()

    def initial_review_selection(self, input_text):
        """
        Collects the feedback from the initial reviewers.

        This function iterates over the list of reviewers and queries their models twice.
        If a reviewer provides a response, it is added to the conversation history.
        If the query fails, an error is logged.

        Args:
            input_text (str): The input text to be reviewed.
        """
        for reviewer in self.reviewers:
            if self.iteration_id != "0":
                rag_content = self.conversational_rag.retrieve_full_history(self.conversation_id)
                if rag_content is None:
                    self.reset_iteration()
                    self.error_logger.add_error(f"Unable to retrieve RAG's content during the iteration number {self.iteration_id}.")
                    raise RetrievalRAGException(f"Unable to retrieve RAG's content during the iteration number {self.iteration_id}.")
                reviewer.set_full_prompt(reviewer.get_instructions(), input_text, rag_content)
            else:
                reviewer.set_full_prompt(reviewer.get_instructions(), input_text)
            reviewer_response = reviewer.query_model()
            if reviewer_response is None:
                self.error_logger.add_error(f"An error occurred while communicating with {reviewer.get_name()} during the first step.")
            elif reviewer_response is not None:
                message = Message(reviewer.get_name(), reviewer_response)
                self.conversation.add_message(message)

    def subsequent_rounds(self, input_text) -> None:
        """
        Conducts subsequent review rounds by querying reviewers with updated conversation history.

        This function iterates over the reviewers and updates their prompts using the
        conversation history. Each reviewer is allowed to respond once per iteration.
        If a reviewer fails to respond, an error is logged, and the process continues.

        Note: The number of iterations and allowed responses per reviewer are currently
        set to 1 but can be increased when a more capable LLM is available.

        Returns:
            None
        """
        for reviewer in self.reviewers:
            if self.iteration_id != "0":
                rag_content = self.conversational_rag.retrieve_full_history(self.conversation_id)
                if rag_content is None:
                    self.reset_iteration()
                    self.error_logger.add_error(f"Unable to retrieve RAG's content during the iteration number {self.iteration_id}.")
                    raise RetrievalRAGException(f"Unable to retrieve RAG's content during the iteration number {self.iteration_id}.")
                integrated_data = self.integrate_rag_and_history(rag_content, self.conversation.get_history())
                reviewer.set_full_prompt(reviewer.get_instructions(), input_text, integrated_data) #todo: also in this case the input_text (the problem presented in the CR) should be included
            else:
                reviewer.set_full_prompt(reviewer.get_instructions(), input_text, self.conversation.get_history())
            if reviewer.get_iteration_messages() < self.messages_per_iteration: #todo: this check can be potentially removed since the for guarantees already 2 messages max per agent
                reviewer_response = reviewer.query_model()
                if reviewer_response is None:
                    self.error_logger.add_error(f"An error occurred wile trying to communicate with {reviewer.get_name()}.")
                    self.from_agent_get_errors(reviewer)
                    reviewer_response = "" #the reviewers are non-blocking: if some user do not respond, the conversation will continue
                reviewer.increment_iteration_messages()
                message = Message(reviewer.get_name(), reviewer_response)
                self.conversation.add_message(message)

    def simulate_conversation(self, cr_task: str = None, input_text: str = None) -> None:
        self.ensure_conversation_path() #ensures that the conversation's folder path exists

        print("Starting the execution of CRANE")
        self.ensure_iteration_path() #ensures that the iteration's folder path exists
        self.simulate_iteration(f"CHANGE REQUEST TASK: {cr_task}; Current problem: {input_text}") #simulates the iteration
        self.check_stopping_condition() #checks if the stopping condition is reached
        self.save_errors()

        for i in range (0, 2):
        #while not self.stopping_condition:
            print(f"Entering in the iteration number {self.get_iteration_id()}")
            self.ensure_iteration_path() # ensures that the iteration's folder path exists
            summarized_history = self.summarize_iteration_history() #summarizes the previous iteration's history
            #print(f"CHANGE REQUEST TASK: {cr_task}; Current problem: {input_text}")
            current_input_text = self.fetch_model_feedback(summarized_history, input_text) #provides the summarized history as a feedback to the model
            self.simulate_iteration(f"CHANGE REQUEST TASK: {cr_task}; Current problem: {current_input_text}")  # simulates the iteration
            self.check_stopping_condition()  # checks if the stopping condition is reached
            self.save_errors()
            input_text = current_input_text

        self.increment_conversation_id()
        self.reset_iteration()

    def fetch_model_feedback(self, summarized_history, input_text) -> str:
        """
        Fetches feedback from the model based on the agent's instructions and history.

        This method constructs a prompt using the agent's instructions and history.
        If a response is successfully retrieved, it is returned immediately.

        Returns:
            str: The feedback response from the model.
        """
        task = f"Actionable insights: {summarized_history} \n\n Code to work on: {input_text}"
        self.feedback_agent.set_full_prompt(self.feedback_agent.get_instructions(), task)
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
                save_state = self.conversational_rag.save_iteration(self.conversation_id, self.iteration_id, summarized_response)
                if save_state == 0:
                    self.reset_iteration()
                    self.error_logger.add_error(f"Failed to save messages to RAG (iteration_id={self.iteration_id}).")
                    raise SaveRAGException(f"Failed to save messages to RAG (iteration_id={self.iteration_id}).")
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

    def get_conversational_rag(self):
        return self.conversational_rag

    def integrate_rag_and_history(self, rag_content, history):
        """
        Integrates retrieved RAG content with the existing conversation history.

        Converts each RAG (Retrieval-Augmented Generation) content item into a message
        format consistent with the conversation history, labeling the sender as "RAG".
        The new RAG messages are then appended to the existing history.

        Args:
            rag_content (list): A list of strings representing content retrieved via RAG.
            history (list): A list of existing message dictionaries in the format
                            [{"sender": str, "content": str}, ...].

        Returns:
            list: A combined list of message dictionaries including the original history
                  and the newly formatted RAG content.
        """
        rag_as_history = [{"sender": "RAG", "content": content} for content in rag_content]
        integrated_data = history + rag_as_history

        return integrated_data