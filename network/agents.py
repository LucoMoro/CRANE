import os

from network.huggingface_api import query_huggingface_model
from network.config import conversations_path
from network.utils import ensure_conversation_path, get_iteration_id

iteration_id = get_iteration_id()
conversation_path = ensure_conversation_path(conversations_path, iteration_id)

with open(f'{conversations_path}conversation_1/iteration_1/test_prompt', 'r') as file_in:
        question = file_in.read()

response = query_huggingface_model(question)

if response:
    with open(f'{conversations_path}conversation_1/iteration_{iteration_id}/response', 'w', encoding='utf-8') as file_out:
        file_out.write(response[0]["generated_text"])
