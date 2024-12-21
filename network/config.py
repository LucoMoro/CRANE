import os

from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("HUGGINGFACE_API_KEY")

headers = {
    "Authorization": f"Bearer {api_key}"
}
