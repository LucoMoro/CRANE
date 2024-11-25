import os

from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("HUGGINGFACE_API_KEY")

folder_path = "../conversations/"

model_id = "distilgpt2"
api_url = f"https://api-inference.huggingface.co/models/{model_id}"
headers = {
    "Authorization": f"Bearer {api_key}"
}
