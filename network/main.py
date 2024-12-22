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

"""
conversation_id = conversation.get_conversation_id()
iteration_path = f"../conversations/conversation_{conversation_id}/iteration_id"
iteration_id = conversation.get_iteration_id(iteration_path)
conversation_path = conversation.ensure_conversation_path()

response1 = moderator.query_model()
response2 = reviewer1.query_model()

message1 = Message(moderator.get_name(),response1)
message2 = Message(reviewer1.get_name(),response2)

conversation.add_message(message1)
conversation.add_message(message2)

conversation.save_model_responses(conversation.get_history())
iteration_id = int(iteration_id)
iteration_id += 1
conversation.set_iteration_id(str(iteration_id), iteration_path)
"""

conversation.simulate_iteration("")



