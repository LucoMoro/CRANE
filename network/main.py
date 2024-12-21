from network.agents.moderator import Moderator
from network.agents.reviewer import Reviewer
from network.config import conversations_path, agent_id, responses
from network.utils import ensure_conversation_path, save_model_responses
from network.communication.conversation import Conversation

moderator = Moderator("../prompts/system_prompt_1/moderator.json")
reviewer1 = Reviewer("../prompts/system_prompt_1/reviewer_1.json")
reviewer2 = Reviewer("../prompts/system_prompt_1/reviewer_2.json")
reviewer3 = Reviewer("../prompts/system_prompt_1/reviewer_3.json")
reviewer4 = Reviewer("../prompts/system_prompt_1/reviewer_4.json")

reviewers = [reviewer1, reviewer2, reviewer3, reviewer4]

conversation = Conversation(moderator, reviewers)


conversation_id = conversation.get_conversation_id()
iteration_path = f"../conversations/conversation_{conversation_id}/iteration_id"
iteration_id = conversation.get_iteration_id(iteration_path)
conversation_path = ensure_conversation_path(conversations_path, conversation_id, iteration_id)

response = moderator.query_model()

save_model_responses(conversation_id, iteration_id, response)
iteration_id = int(iteration_id)
iteration_id += 1
conversation.set_iteration_id(str(iteration_id), iteration_path)




