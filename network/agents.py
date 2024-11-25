from network.huggingface_api import query_huggingface_model
from network.config import folder_path

with open(f'{folder_path}conversation_1/iteration_1/test_prompt', 'r') as file_in:
        question = file_in.read()

response = query_huggingface_model(question)

if response:
    with open(f'{folder_path}conversation_1/iteration_1/response', 'w', encoding='utf-8') as file_out:
        file_out.write(response[0]["generated_text"])
