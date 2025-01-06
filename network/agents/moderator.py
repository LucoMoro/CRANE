from network.agents.agent_base import AgentBase


class Moderator(AgentBase):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.agents_specialization = None
        self.summarization_prompt = "i am so happy because..."

    def set_agents_specialization(self, agents_specialization) -> None:
        self.agents_specialization = agents_specialization

    def get_agent_specialization(self) -> list[str]:
        return self.agents_specialization

    def get_summarization_prompt(self) -> str:
        return self.summarization_prompt

    def set_summarization_prompt(self, summarization_prompt):
        self.summarization_prompt = summarization_prompt