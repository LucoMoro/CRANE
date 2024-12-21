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