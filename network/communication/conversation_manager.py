import os
import json

from network.agents.agent_base import AgentBase
from network.communication.conversation import Conversation
from network.communication.message import Message
from network.config import base_path
from network.utils.error_logger import ErrorLogger
from network.communication.conversational_rag import ConversationalRAG


class ConversationManager:
    def __init__(self, conversation: Conversation, max_retries: int = None, messages_per_iteration: int = None, human_role: str = "", human_flag: bool = False):
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
            self.messages_per_iteration = 2
        else:
            self.messages_per_iteration = messages_per_iteration

        self.error_logger = ErrorLogger()
        self.error_state = False
        self.cr_name = ""

        self.human_role = human_role
        self.human_flag = human_flag

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

    def save_non_reviewer_response(self, message, file_name: str) -> None:
        """
        Saves the response of the moderator/feedback agent as a JSON file in the current iteration's directory.

        Args:
            message: The messages to save. It is expected to be an instance of the Message class.
            file_name (str): the name of the json file in which the response has to be saved
        """
        full_path = os.path.join(self.base_path, f"conversation_{self.get_conversation_id()}/iteration_{self.get_iteration_id()}")
        saving_file = os.path.join(full_path, f"{file_name}.json")
        data = {
            "conversation_id": self.conversation_id,
            "iteration_id": self.iteration_id,
            "response": [message]
        }
        with open(saving_file, "w") as output:
            json.dump(data, output, indent=4)

    def save_errors(self) -> None:
        full_path = os.path.join(self.base_path, f"conversation_{self.conversation_id}/iteration_{self.iteration_id}")
        errors_file = os.path.join(full_path, "errors.txt")

        with open (errors_file, "w") as output:
            output.write(self.error_logger.from_array_to_text(f"iteration n.{self.iteration_id}"))
        return None

    def simulate_iteration(self, input_text: str = None) -> None:
        """
        This method orchestrates the entire conversation flow, simulating
        a full iteration of the conversation process, consisting of an
        initial review selection followed by a series of predefined message rounds.
        After completing all rounds, it saves the generated responses from the model
        and resets the messages for the next iteration.

        Args:
            input_text (str, optional): The input text to initiate the conversation.
            If not provided (None), a default or pre-existing input will be used.
            This input serves as the starting point for the conversation iteration.

        Returns:
            None
        """

        self.initial_review_selection(input_text)
        if self.error_state:
            return None
        for i in range(0, self.messages_per_iteration):
            self.subsequent_rounds(input_text)
            if self.error_state:
                return None

        self.save_model_responses(self.conversation.get_history())
        self.reset_iteration_messages()

    def initial_review_selection(self, input_text):
        """
            Performs the initial review selection process by querying the designated reviewers
            and retrieving relevant RAG (retrieval-augmented generation) content if applicable.

            The function first checks whether the current iteration is not the initial one.
            If it's not the first iteration, it attempts to retrieve the full RAG content
            from the conversation history. If retrieval fails, an error is logged, and the
            iteration is reset. For each reviewer, the function sets the full prompt based
            on the input text, and if applicable, the retrieved RAG content.
            It then sends the full prompt to the reviewer's model and handles the response.

            If a response is received, it is added as a message to the history conversation.
            If no response is received or an error occurs, an error message is logged.

            Args:
                input_text (str): The text to be reviewed and sent to the reviewers.

            Raises:
                RetrievalRAGException: If RAG content retrieval fails during a non-initial iteration.
            """
        rag_content = ""
        if self.iteration_id != "0":
            rag_content = self.conversational_rag.retrieve_full_history(self.conversation_id)
            if rag_content is None:
                self.stop_simulation(f"Unable to retrieve RAG's content during the iteration number {self.iteration_id}.")
                return None
                #raise RetrievalRAGException(f"Unable to retrieve RAG's content during the iteration number {self.iteration_id}.")

        for reviewer in self.reviewers:
            if self.iteration_id != "0":
                reviewer.set_additional_context(rag_content)
                reviewer.set_input_problem(input_text)
            else:
                reviewer.set_input_problem(input_text)
            reviewer_response = reviewer.query_model()
            if reviewer_response is None:
                self.error_logger.add_error(f"An error occurred while communicating with {reviewer.get_name()} during the first step.")
                self.from_agent_get_errors(reviewer, "  ")
                reviewer.set_error_logger([])
            elif reviewer_response is not None:
                message = Message(reviewer.get_name(), reviewer_response)
                self.conversation.add_message(message)

        if self.human_flag == True and self.human_role == "reviewer":
            print("   >>> Now it's your turn as Reviewer.")
            print(f"   >>> Additional RAG informations are is: {rag_content}")
            print(f"   >>> The CR is: {input_text}")
            reviewer_response = input("   >>> Answer:")
            message = Message("Human Reviewer", reviewer_response)
            self.conversation.add_message(message)

    def subsequent_rounds(self, input_text) -> None:
        """
        Conducts subsequent review rounds by querying reviewers with the updated conversation history.

        This function iterates over the list of reviewers, updating their prompts with the
        conversation history (and potentially RAG content). Each reviewer is allowed to respond
        once per iteration. If a reviewer fails to respond or encounters an error, an error is logged,
        and the process continues. This ensures the review process proceeds even if individual reviewers
        do not provide a response.

        The number of iterations and the number of responses per reviewer are currently limited to 1
        but can be adjusted in the future based on system capabilities.

        Args:
            input_text (str): The text to be reviewed and sent to the reviewers.

        Returns:
            None

        Raises:
            RetrievalRAGException: If the RAG content retrieval fails during a non-initial iteration.
        """
        rag_content = ""
        if self.iteration_id != "0":
            rag_content = self.conversational_rag.retrieve_full_history(self.conversation_id)
            if rag_content is None:
                self.stop_simulation(f"Unable to retrieve RAG's content during the iteration number {self.iteration_id}.")
                return None
                #raise RetrievalRAGException(f"Unable to retrieve RAG's content during the iteration number {self.iteration_id}.")

        for reviewer in self.reviewers:
            if self.iteration_id != "0":
                integrated_data = self.integrate_rag_and_history(rag_content, self.conversation.get_history())
                reviewer.set_additional_context(integrated_data)
                reviewer.set_input_problem(input_text)
            else:
                reviewer.set_additional_context(self.conversation.get_history())
                reviewer.set_input_problem(input_text)
            reviewer_response = reviewer.query_model()
            if reviewer_response is None:
                self.error_logger.add_error(f"An error occurred wile trying to communicate with {reviewer.get_name()}.")
                self.from_agent_get_errors(reviewer, "  ")
                reviewer.set_error_logger([])
                reviewer_response = "" #the reviewers' messages are non-blocking: if a reviewer does not respond, the conversation will continue
            reviewer.increment_iteration_messages()
            message = Message(reviewer.get_name(), reviewer_response)
            self.conversation.add_message(message)

        if self.human_flag == True and self.human_role == "reviewer":
            print("   >>> Now it's your turn as Reviewer.")
            print(f"   >>> The conversation is: {self.conversation.get_history()}")
            print(f"   >>> Additional RAG informations are is: {rag_content}")
            print(f"   >>> The CR is: {input_text}")
            reviewer_response = input("   >>> Answer:")
            message = Message("Human Reviewer", reviewer_response)
            self.conversation.add_message(message)

    def simulate_conversation(self, cr_task: str = None, input_text: str = None) -> None:
        """
        Simulates a conversation process for a given change request task and input text over multiple iterations.

        This function starts the conversation simulation by ensuring the necessary folder paths exist for both the
        conversation and iteration. It proceeds with the first iteration based on the provided `cr_task` (change request task)
        and `input_text`. After simulating the iteration, it summarizes the iteration history and provides the feedback
        to the model. The simulation continues for up to n iterations, or until a stopping condition is met.

        In each iteration, the history of the previous iteration is summarized, and the model receives the feedback
        for generating updated input text. If a stopping condition is not met, the iteration continues until the limit is reached.

        Args:
            cr_task (str, optional): The description of the change request task to be simulated. Defaults to None.
            input_text (str, optional): The current problem or input text that the conversation is centered around. Defaults to None.

        Returns:
            None

        Notes:
            - The simulation process involves multiple iterations, and the stopping condition must be explicitly checked.
            - The conversation and iteration folder paths are ensured before each iteration.
            - The simulation proceeds for a maximum of n iterations unless the stopping condition is satisfied earlier.
            - Errors encountered during the simulation are logged and saved.
            - The iteration ID is incremented with each cycle, and the conversation ID is incremented once the simulation is complete.
            - The `simulate_iteration` method is used to simulate each iteration based on the current input text and summarized history.
        """

        self.ensure_conversation_path() #ensures that the conversation's folder path exists

        print(f"(conversation {self.conversation_id}): Starting the execution of CRANE for {self.cr_name}")
        print(f"   Entering in the iteration number {self.get_iteration_id()}")
        self.ensure_iteration_path() #ensures that the iteration's folder path exists
        self.simulate_iteration(f"CHANGE REQUEST TASK: {cr_task}; Current problem: {input_text}") #simulates the iteration
        if self.error_state:
            self.save_errors()
            self.increment_conversation_id()
            return None
        summarized_history = self.summarize_iteration_history()  # summarizes the previous iteration's history
        if self.error_state:
            self.save_errors()
            self.increment_conversation_id()
            return None
        current_input_text = self.fetch_model_feedback(summarized_history, input_text)  # provides the summarized history as a feedback to the model
        if self.error_state:
            self.save_errors()
            self.increment_conversation_id()
            return None
        self.save_errors()
        self.increment_iteration_id()

        i = 0
        while i < 1 and self.stopping_condition == False:
            print(f"   Entering in the iteration number {self.get_iteration_id()}")
            self.error_logger.reset_errors()
            self.ensure_iteration_path() # ensures that the iteration's folder path exists
            self.simulate_iteration(f"### CR_TASK \n{cr_task}\n\n ### Code snippet\n{current_input_text}")  # simulates the iteration
            if self.error_state:
                self.save_errors()
                self.increment_conversation_id()
                return None
            self.check_stopping_condition()  # checks if the stopping condition is reached
            if not self.stopping_condition:
                summarized_history = self.summarize_iteration_history()  # summarizes the previous iteration's history
                if self.error_state:
                    self.save_errors()
                    self.increment_conversation_id()
                    return None
                current_input_text = self.fetch_model_feedback(summarized_history, current_input_text)  # provides the summarized history as a feedback to the model
                if self.error_state:
                    self.save_errors()
                    self.increment_conversation_id()
                    return None
            self.save_errors()
            self.increment_iteration_id()
            i=i+1

        self.increment_conversation_id()
        self.reset_iteration()

    def fetch_model_feedback(self, summarized_history, input_text) -> str | None:
        """
        Fetches feedback from the model based on the reviewers' suggestions and history.

        This method constructs a prompt by combining the provided summarized history and the
        current input text, then uses the feedback agent to query the model for a response.
        The response is returned immediately if successfully retrieved. If the response is
        not valid or an error occurs, the method retries up to a maximum number of attempts.
        If all attempts fail, an error is logged, the iteration is reset, and an exception is raised.

        Args:
            summarized_history: The summarized history of the conversation.
            input_text: The current problem or input that needs to be addressed in the feedback.

        Returns:
            str: The feedback response from the model, or None if unsuccessful after retries.

        Raises:
            FeedbackException: If the feedback agent fails to provide a valid response after the maximum number of retries.
        """
        if self.human_flag == True and self.human_role == "feedback_agent":
            print("   >>> Now it's your turn as Feedback Agent.")
            print(f"   >>> The Summary of Suggestions is: \n {summarized_history}")
            print(f"   >>> The problem is: {input_text}")
            feedback_response = input("   >>> Answer:")
            feedback_message = Message("Human Feedback Agent", feedback_response)
            self.save_non_reviewer_response(feedback_message.to_dict(), f"change_{self.cr_name}")
            return feedback_response
        else:
            self.feedback_agent.set_additional_context(f"  ## Summary of Suggestions\n{summarized_history}\n\n")
            self.feedback_agent.set_input_problem(f"  ## Current problem\n{input_text}")
            for i in range(0, self.max_retries):
                feedback_response = self.feedback_agent.query_model()
                if feedback_response is None:
                    self.error_logger.add_error(f"Attempt {i}: An error occurred while communicating with the feedback agent.")
                    self.from_agent_get_errors(self.feedback_agent, "   ")
                    self.feedback_agent.set_error_logger([])
                elif feedback_response is not None:
                    feedback_message = Message(self.feedback_agent.get_name(), feedback_response)
                    self.save_non_reviewer_response(feedback_message.to_dict(), f"change_{self.cr_name}")
                    return feedback_response
            self.stop_simulation(f"The feedback agent failed to provide a valid response after {self.max_retries} attempts.")
            return None
        #raise FeedbackException(f"The feedback agent failed to provide a valid response after {self.max_retries} attempts.")

    def summarize_iteration_history(self) -> str | None:
        """
        Summarizes the iteration's history using the moderator.

        This method constructs a summarization prompt using the moderator's summarization prompt
        and the current conversation history. This is sent to the moderator for processing.
        If a valid response is received, the history is cleared to make room for new input, and
        the summarized response is saved in the RAG and then returned. If the summarization fails
        or the moderator doesn't provide a valid response, the method retries up to a maximum number
        of attempts. If all attempts fail, an error is logged, the iteration is reset, and an
        exception is raised.

        Returns:
            str: The summarized response from the moderator model. If no valid response is obtained after retries,
            an empty string is returned.

        Raises:
            SummarizationException: If the moderator fails to provide a valid response after the maximum number of retries.
            SaveRAGException: If saving the summarized history to RAG fails after a successful summarization.
        """
        summarized_response = ""
        if self.human_flag == True and self.human_role == "moderator":
            print(f"   >>> Now it's your turn as Moderator.")
            print(f"   >>> The Suggestions are {self.conversation.get_history()}")
            summarized_response = input(f"   >>> Answer:")
            moderator_message = Message("Human Moderator", summarized_response)
            self.save_non_reviewer_response(moderator_message.to_dict(), "summary")
            self.conversation.set_history([])  # if the history is correctly summarized, the iteration's history will be deleted leaving space for the new one
            save_state = self.conversational_rag.save_iteration(self.conversation_id, self.iteration_id,summarized_response)
            if save_state == 0:
                self.stop_simulation(f"Failed to save messages to RAG (iteration_id={self.iteration_id}).")
                return None
                # raise SaveRAGException(f"Failed to save messages to RAG (iteration_id={self.iteration_id}).")
            return summarized_response
        else:
            self.moderator.set_input_problem(self.conversation.get_history())
            for i in range(0, self.max_retries):
                summarized_response = self.moderator.query_model()
                if summarized_response is None:
                    self.error_logger.add_error(f"Attempt {i}: An error occurred while communicating with the moderator during the summarization of the input.")
                    self.from_agent_get_errors(self.moderator, "   ")
                    self.moderator.set_error_logger([])
                elif summarized_response is not None:
                    moderator_message = Message(self.moderator.get_name(), summarized_response)
                    self.save_non_reviewer_response(moderator_message.to_dict(), "summary")
                    self.conversation.set_history([]) #if the history is correctly summarized, the iteration's history will be deleted leaving space for the new one
                    save_state = self.conversational_rag.save_iteration(self.conversation_id, self.iteration_id, summarized_response)
                    if save_state == 0:
                        self.stop_simulation(f"Failed to save messages to RAG (iteration_id={self.iteration_id}).")
                        return None
                        #raise SaveRAGException(f"Failed to save messages to RAG (iteration_id={self.iteration_id}).")
                    return summarized_response
            self.stop_simulation(f"The moderator failed to provide a valid response after {self.max_retries} attempts.")
            return None
            #raise SummarizationException(f"The moderator failed to provide a valid response after {self.max_retries} attempts.")

    def check_stopping_condition(self) -> None:
        """
        Checks whether the stopping condition for the process has been met.

        Returns:
            bool: returns True if the stopping condition has been met.
        """
        if all(message["content"] == "Another round is not needed." for message in self.conversation.get_history()):
            self.stopping_condition = True
        else:
            self.stopping_condition = False


    def reset_iteration_messages(self) -> None:
        for reviewer in self.reviewers:
            reviewer.set_iteration_messages(0)

    def from_agent_get_errors(self, agent: AgentBase, indent: str = "") -> None:
        """
        Collects error logs from a given agent and adds them to the central error logger.

        Returns:
            None: This method modifies the internal error logger by adding errors retrieved
                  from the provided agent.

        """
        reviewer_errors = agent.get_error_logger()
        for error in reviewer_errors:
            self.error_logger.add_error(f"{indent}{error}")

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

    def stop_simulation(self, message: str):
        self.reset_iteration()
        self.error_logger.add_error(message)
        self.error_state = True

    def get_error_state(self) -> bool:
        return self.error_state

    def set_error_state(self, error_state):
        self.error_state = error_state

    def get_cr_name(self) -> str:
        return self.cr_name

    def set_cr_name(self, cr_name: str):
        self.cr_name = cr_name