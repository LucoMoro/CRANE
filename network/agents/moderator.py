from network.agents.agent_base import AgentBase


class Moderator(AgentBase):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.personality_types = None