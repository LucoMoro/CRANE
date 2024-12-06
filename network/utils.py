import os

def get_iteration_id():
    """
    Reads and returns the current iteration ID from the iteration_id file.

    Returns:
        str: The iteration ID as a string.
    """
    with open("../conversations/conversation_1/iteration_id", "r") as iteration_file:
        return iteration_file.read().strip()

def set_iteration_id(iteration_count):
    """
    Overwrites the ID of the current iteration from the iteration_id file

    Args:
        iteration_count (str): The content to write into the file.
    """
    with open("../conversations/conversation_1/iteration_id", "w") as iteration_file:
        return iteration_file.write(iteration_count)

def get_conversation_id():
    """
    Reads and returns the current conversation ID from the conversation_id file.

    Returns:
        str: The conversation ID as a string.
    """
    with open("../conversations/conversation_id", "r") as conversation_file:
        return conversation_file.read().strip()

def set_conversation_id(conversation_count):
    """
    Overwrites the ID of the current conversation from the conversation_id file

    Args:
        conversation_count (str): The content to write into the file.
    """
    with open("../conversations/conversation_id", "w") as conversation_file:
        return conversation_file.write(conversation_count)


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

