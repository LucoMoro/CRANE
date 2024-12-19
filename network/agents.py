from network.agents.agent_base import AgentBase
from network.huggingface_api import query_huggingface_model
from network.config import conversations_path, agent_id, responses
from network.utils import ensure_conversation_path, save_model_responses
from network.utils import get_iteration_id, set_iteration_id, get_conversation_id

agent = AgentBase("../prompts/system_prompt_1/moderator.json").print()


"""
conversation_id = get_conversation_id()
iteration_path = f"../conversations/conversation_{conversation_id}/iteration_id"
iteration_id = get_iteration_id(iteration_path)
conversation_path = ensure_conversation_path(conversations_path, conversation_id, iteration_id)


with open(f'{conversations_path}conversation_1/iteration_0/test_prompt', 'r') as file_in:
        question = file_in.read()


while agent_id < 5:
    response = query_huggingface_model(question)

    if response:
        responses.append(response[0]['generated_text'])
        agent_id += 1


model_responses = {
    "agent_1": responses[0],
    "agent_2": responses[1],
    "agent_3": responses[2],
    "agent_4": responses[3]
}
save_model_responses(conversation_id, iteration_id, model_responses)
iteration_id = int(iteration_id)
iteration_id += 1
set_iteration_id(str(iteration_id), iteration_path)
"""



