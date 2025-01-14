from network.agents.agent_base import AgentBase
from network.agents.moderator import Moderator
from network.agents.reviewer import Reviewer
from network.communication.conversation import Conversation
from network.communication.conversation_manager import ConversationManager
from network.communication.message import Message

moderator = Moderator("../prompts/system_prompt_1/moderator.json")
reviewer1 = Reviewer("../prompts/system_prompt_1/reviewer_1.json")
reviewer2 = Reviewer("../prompts/system_prompt_1/reviewer_2.json")
reviewer3 = Reviewer("../prompts/system_prompt_1/reviewer_3.json")
reviewer4 = Reviewer("../prompts/system_prompt_1/reviewer_4.json")
reviewers = [reviewer1, reviewer2, reviewer3, reviewer4]

feedback_agent = AgentBase("../prompts/system_prompt_1/feedback_agent.json")

conversation = Conversation(moderator, reviewers, feedback_agent)

conversation_manager = ConversationManager(conversation)

#response_message = Message("test_1", "test i am writing something In RESPONSE tO: reviewer_1 to test the new feature CAPS TEST")
#conversation.add_message(response_message)

#response_message1 = Message("test_2", "test i am writing something in response to: reviewer_3 to test the new feature CAPS TEST")
#conversation.add_message(response_message1)

conversation_manager.simulate_conversation("")

