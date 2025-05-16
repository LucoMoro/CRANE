import json
import os

from network.config import dataset_path
from network.agents.agent_base import AgentBase
from network.agents.moderator import Moderator
from network.agents.reviewer import Reviewer
from network.communication.conversation import Conversation
from network.communication.conversation_manager import ConversationManager
from network.communication.message import Message

def conversation_setup():
    moderator = Moderator("../prompts/system_prompt_4/moderator.json")
    reviewer1 = Reviewer("../prompts/system_prompt_4/reviewer_1.json")
    reviewer2 = Reviewer("../prompts/system_prompt_4/reviewer_2.json")
    reviewer3 = Reviewer("../prompts/system_prompt_4/reviewer_3.json")
    reviewers = [reviewer1, reviewer2, reviewer3]

    feedback_agent = AgentBase("../prompts/system_prompt_4/feedback_agent.json")

    conversation = Conversation(moderator, reviewers, feedback_agent)
    return conversation

def main(conversation):
    snippets_folder = os.path.join(dataset_path, "snippets")
    tasks_description_folder = os.path.join(dataset_path, "tasks_description")
    snippets = os.listdir(snippets_folder)
    tasks_description = os.listdir(tasks_description_folder)
    conversation_outcome = ""

    for i in range (0, 25):
        try:
            conversation_manager = ConversationManager(conversation)
        except Exception as e:
            print(f"[Pinecone Error] The file {i} will not be executed. Error cause: {e}")
            continue

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

        #print(f"Snippet file {snippets[i]}")
        #print(f"Task file {tasks_description[i]}")
        cr_name, _ = os.path.splitext(snippets[i])
        filtered_cr_name = cr_name.replace("before_", "")
        #print(filtered_cr_name)
        conversation_manager.set_cr_name(filtered_cr_name)
        conversation_manager.simulate_conversation(task, snippet_data)

        error_state = conversation_manager.get_error_state()
        if error_state:
            conversation_outcome = f"   An error occurred during the conversation n. {int(conversation_manager.get_conversation_id())-1} while executing the snippet {snippets[i]}."
        else:
            conversation_outcome = f"   No errors occurred during the conversation n. {int(conversation_manager.get_conversation_id())-1} while executing the snippet {snippets[i]}."
        print(conversation_outcome)
        print("=======================================================================================================")


if __name__ == "__main__":
    conv = conversation_setup()
    main(conv)