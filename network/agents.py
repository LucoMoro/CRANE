from network.agents.agent_base import AgentBase
from network.agents.moderator import Moderator
from network.config import conversations_path, agent_id, responses
from network.utils import ensure_conversation_path, save_model_responses
from network.utils import get_iteration_id, set_iteration_id, get_conversation_id

agent = Moderator("../prompts/system_prompt_1/moderator.json")

conversation_id = get_conversation_id()
iteration_path = f"../conversations/conversation_{conversation_id}/iteration_id"
iteration_id = get_iteration_id(iteration_path)
conversation_path = ensure_conversation_path(conversations_path, conversation_id, iteration_id)

response = agent.query_model()

agent.print()

save_model_responses(conversation_id, iteration_id, response)
iteration_id = int(iteration_id)
iteration_id += 1
set_iteration_id(str(iteration_id), iteration_path)


