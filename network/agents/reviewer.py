from network.agents.agent_base import AgentBase


class Reviewer(AgentBase):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.iteration_messages = 0

    def get_specialization(self) -> str:
        return self.specialization

    def get_iteration_messages(self) -> int:
        return self.iteration_messages

    def set_iteration_messages(self, value: int) -> None:
        self.iteration_messages = value

    def increment_iteration_messages(self) -> None:
        self.iteration_messages = self.iteration_messages + 1

    def get_personality(self) -> str:
        return self.personality

    def set_personality(self, new_personality: str) -> None:
        self.personality = new_personality