import requests

from network.config import api_url, headers

def query_huggingface_model(question):
    """
    Sends a question to a Hugging Face model via a POST request and returns the model's response.

    Parameters:
    ----------
    question : str
        The question or input text to send to the Hugging Face model.

    Returns:
    -------
    dict or None
        If the request is successful (status code 200), returns the response from the model as a dictionary.
        If the request fails, prints an error message with the status code and error details, and returns None.

    Notes:
    -----
    This function assumes that `api_url` (the endpoint URL of the Hugging Face model) and `headers`
    (the request headers, including any required authorization) are defined elsewhere in the code.
    """
    response = requests.post(api_url, headers= headers, json={"inputs": question})

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Errore {response.status_code}: {response.text}")
        return None