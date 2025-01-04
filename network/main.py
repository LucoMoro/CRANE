from network.agents.moderator import Moderator
from network.agents.reviewer import Reviewer
from network.communication.conversation import Conversation
from network.communication.message import Message

moderator = Moderator("../prompts/system_prompt_1/moderator.json")
reviewer1 = Reviewer("../prompts/system_prompt_1/reviewer_1.json")
reviewer2 = Reviewer("../prompts/system_prompt_1/reviewer_2.json")
reviewer3 = Reviewer("../prompts/system_prompt_1/reviewer_3.json")
reviewer4 = Reviewer("../prompts/system_prompt_1/reviewer_4.json")
reviewers = [reviewer1, reviewer2, reviewer3, reviewer4]

conversation = Conversation(moderator, reviewers)

#response_message = Message("test_1", "i am writing something to test the new feature. In response to: reviewer_1 test")
#conversation.add_message(response_message)

conversation.simulate_conversation("")



