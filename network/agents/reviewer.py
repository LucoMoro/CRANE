from network.agents.agent_base import AgentBase


class Reviewer(AgentBase):
    def __init__(self, file_path):
        super().__init__(file_path)


    def get_type(self) -> str:
        return self.type