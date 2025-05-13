import json
import os

from network.config import dataset_path
from network.agents.agent_base import AgentBase
from network.agents.moderator import Moderator
from network.agents.reviewer import Reviewer
from network.communication.conversation import Conversation
from network.communication.conversation_manager import ConversationManager
from network.communication.message import Message

moderator = Moderator("../prompts/system_prompt_1/moderator.json")
reviewer1 = Reviewer("../prompts/system_prompt_1/reviewer_1.json")
reviewer2 = Reviewer("../prompts/system_prompt_1/reviewer_2.json")
#reviewer3 = Reviewer("../prompts/system_prompt_1/reviewer_3.json")
#reviewer4 = Reviewer("../prompts/system_prompt_1/reviewer_4.json")
#reviewers = [reviewer1, reviewer2, reviewer3, reviewer4]
reviewers = [reviewer1, reviewer2]

feedback_agent = AgentBase("../prompts/system_prompt_1/feedback_agent.json")

conversation = Conversation(moderator, reviewers, feedback_agent)

#response_message = Message("test_1", "test i am writing something In RESPONSE tO: reviewer_1 to test the new feature CAPS TEST")
#conversation.add_message(response_message)

#response_message1 = Message("test_2", "test i am writing something in response to: reviewer_3 to test the new feature CAPS TEST")
#conversation.add_message(response_message1)

#conversation_manager.get_conversational_rag().clear_all_data()

snippets_folder = os.path.join(dataset_path, "snippets")
tasks_description_folder = os.path.join(dataset_path, "tasks_description")

snippets = os.listdir(snippets_folder)
tasks_description = os.listdir(tasks_description_folder)

for i in range (0, 1):
    conversation_manager = ConversationManager(conversation)
    task_description_data = ""
    snippet_data = ""
    snippet_path = os.path.join(snippets_folder, snippets[i])
    try:
        with open(snippet_path, "r") as snippet:
            snippet_data = snippet.read()
    except FileNotFoundError:
        print(f"Error: File {snippets[i]} not found")

    task_description_path = os.path.join(tasks_description_folder, tasks_description[i])
    try:
        with open(task_description_path, "r") as task_description:
            task_description_data = json.load(task_description)
            task = task_description_data.get("cr_task", "")
    except FileNotFoundError:
        print(f"Error: File {snippets[i]} not found")

    print(f"Snippet file {snippets[i]}")
    print(f"Task file {tasks_description[i]}")
    conversation_manager.simulate_conversation(task, snippet_data)

#conversation_manager.simulate_conversation()

#rag_content = conversation_manager.get_conversational_rag().retrieve_full_history(str(int(conversation_manager.get_conversation_id())-1))
#print(f"test {rag_content}")