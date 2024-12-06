import os

from network.huggingface_api import query_huggingface_model
from network.config import conversations_path, agent_id, responses
from network.utils import ensure_conversation_path, get_iteration_id, set_iteration_id

iteration_id = get_iteration_id()
conversation_path = ensure_conversation_path(conversations_path, iteration_id)


with open(f'{conversations_path}conversation_1/iteration_0/test_prompt', 'r') as file_in:
        question = file_in.read()

while agent_id < 5:
    response = query_huggingface_model(question)

    if response:
        responses.append(response)
        with open(f'{conversation_path}/response_{agent_id}', 'w', encoding='utf-8') as file_out:
            file_out.write(response[0]["generated_text"])

    agent_id += 1

iteration_id = int(iteration_id)
iteration_id += 1
set_iteration_id(str(iteration_id))
