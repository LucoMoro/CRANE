from network.huggingface_api import query_huggingface_model

with open('../prompts/test_prompt', 'r') as file_in:
        question = file_in.read()

response = query_huggingface_model(question)

if response:
    with open('../conversations/response', 'w', encoding='utf-8') as file_out:
        file_out.write(response[0]["generated_text"])
