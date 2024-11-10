from network.huggingface_api import query_huggingface_model

question = "There was a time when all dragons"
response = query_huggingface_model(question)

if response:
    generated_text = response[0]["generated_text"]
    print("Testo generato:", generated_text)