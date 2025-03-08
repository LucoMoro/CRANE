import os

from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
huggingface_api_key = os.getenv("huggingface_API_KEY")
base_path = os.getenv("BASE_PATH")
pinecone_key = os.getenv("PINECONE_KEY")

openai_headers = {
    "Authorization": f"Bearer {openai_api_key}"
}

huggingface_headers = {
    "Authorization": f"Bearer {huggingface_api_key}"
}