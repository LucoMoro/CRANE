from network.agents.agent_base import AgentBase


class Moderator(AgentBase):
    def __init__(self, file_path, summarization_prompt: str = None):
        super().__init__(file_path)
        self.agents_specialization = None
        if summarization_prompt is None:
            self.summarization_prompt = """
            Your task is to summarize the feedback from multiple reviewers on a given iteration of a code review. Your summary should comprehensively capture all suggestions made, regardless of repetition. Do not omit points simply because they were not mentioned multiple times. Maintain a structured format that clearly presents all feedback in an actionable manner.

            Follow these guidelines:

            - Capture All Key Issues & Suggestions: Ensure that every unique issue raised is included in your summary. If multiple reviewers point out the same issue, note it as a widely agreed-upon concern.
            - Preserve Technical Accuracy: Do not alter the technical details of the reviewers' suggestions. If there are contradictions or ambiguities, highlight them for further clarification.
            - Use a Clear and Organized Format: Structure the summary into key categories (e.g., 'Common Errors', 'Corrections Suggested', 'Potential Contradictions', etc.) so that the person modifying the code can quickly grasp the key points.
            - No Attribution to Specific Reviewers: The summary should be neutral, treating all suggestions equally without referring to individual reviewers by name.
            - Summarize Efficiently but Thoroughly: Aim for conciseness while ensuring completeness. Do not oversimplify to the point of omitting crucial details."""
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