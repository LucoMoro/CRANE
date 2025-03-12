from network.agents.agent_base import AgentBase


class Moderator(AgentBase):
    def __init__(self, file_path, summarization_prompt: str = None):
        super().__init__(file_path)
        self.agents_specialization = None
        if summarization_prompt is None:
            self.summarization_prompt = """
            Your task is to summarize the feedback from multiple reviewers on a given iteration of a code review. Your summary should comprehensively capture all suggestions while remaining as concise as possible. Do not omit points simply because they were not mentioned multiple times.

            Follow these guidelines:

            - Capture All Key Issues & Suggestions: Ensure every unique issue raised is included, but consolidate similar points.
            - Preserve Technical Accuracy: Do not alter the technical details of suggestions. If contradictions exist, highlight them.
            - Use a Clear and Organized Format: Structure feedback into concise bullet points under categories like 'Common Errors' and 'Corrections Suggested.'
            - No Attribution to Specific Reviewers: The summary should be neutral and not refer to individual reviewers.
            - Summarize Efficiently: Use precise language. Avoid unnecessary elaboration while ensuring clarity.
            - Avoid superfluous text: Avoid providing examples, even if they were extracted from the reviewers
            - Limit Response Length: The response must fit within 200 tokens. Prioritize the most critical issues if necessary.
            """
        else:
            self.summarization_prompt = summarization_prompt

    def set_agents_specialization(self, agents_specialization) -> None:
        self.agents_specialization = agents_specialization

    def get_agent_specialization(self) -> list[str]:
        return self.agents_specialization

    def get_summarization_prompt(self) -> str:
        return self.summarization_prompt

    def set_summarization_prompt(self, summarization_prompt):
        self.summarization_prompt = summarization_prompt