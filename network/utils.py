import json
import os



def set_automated_conversation_id(conversation_count):
    """
    Overwrites the ID of the current conversation from the conversation_id file

    Args:
        conversation_count (str): The content to write into the file.
    """
    with open("../conversations/conversation_id", "w") as conversation_file:
        return conversation_file.write(conversation_count)

def set_manual_conversation_id(manual_conversation_count):
    """
    Overwrites the ID of the current conversation with the ID given in input

    Args:
        manual_conversation_count (str): The content to write into the file.
    """
    with open("../conversations/conversation_id", "w") as conversation_file:
        return conversation_file.write(manual_conversation_count)


def ensure_conversation_path(conversations_path, conversation_id, iteration_id):
    """
    Ensures that a directory for the given conversation iteration exists.

    If the directory does not exist, it creates the directory at the specified
    path. The path is constructed using the base conversations_path and the
    iteration_id.

    Args:
        conversations_path (str): The base path for all conversations.
        conversation_id (str): The ID of the current conversation.
        iteration_id (str): The ID of the current iteration.

    Returns:
        str: The full path to the conversation iteration directory.
    """
    conversation_path = f"{conversations_path}conversation_{conversation_id}/iteration_{iteration_id}"
    existing_path = os.path.exists(conversation_path)
    if not existing_path:
        os.makedirs(conversation_path)
    return conversation_path

def save_model_responses(conversation_id, iteration_id, model_responses):
    """
    Saves the model responses for a specific conversation and iteration.

    This function creates a JSON file containing the model's responses,
    along with metadata about the conversation and iteration.

    Args:
        conversation_id (str): The ID of the current conversation.
        iteration_id (str): The ID of the current iteration.
        model_responses (list): A list of responses from the model.

    Returns:
        None
    """
    responses_iteration_path = f"../conversations/conversation_{conversation_id}/iteration_{iteration_id}"
    output_file = os.path.join(responses_iteration_path, "responses.json")

    data = {
        "conversation_id": conversation_id,
        "iteration_id": iteration_id,
        "responses": model_responses
    }

    with open(output_file, "w") as output:
        json.dump(data, output, indent=4)