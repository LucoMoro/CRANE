from network.agents.agent_base import AgentBase
from network.agents.moderator import Moderator
from network.agents.reviewer import Reviewer
from network.communication.message import Message

class Conversation:
    def __init__(self, moderator: Moderator, reviewers: list[Reviewer], feedback_agent: AgentBase):
        self.moderator = moderator
        self.reviewers = reviewers
        self.feedback_agent = feedback_agent
        self.history = []

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

    def set_history(self, new_history) -> None:
        self.history = new_history

    def get_moderator(self) -> Moderator:
        return self.moderator

    def set_moderator(self, new_moderator: Moderator) -> None:
        self.moderator = new_moderator

    def get_reviewers(self) -> list[Reviewer]:
        return self.reviewers

    def set_reviewers(self, new_reviewers: list[Reviewer]) -> None:
        self.reviewers = new_reviewers

    def get_feedback_agent(self) -> AgentBase:
        return self.feedback_agent

    def set_feedback_agent(self, new_feedback_agent: AgentBase ):
        self.feedback_agent = new_feedback_agent