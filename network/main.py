from network.agents.agent_base import AgentBase
from network.agents.moderator import Moderator
from network.agents.reviewer import Reviewer
from network.communication.conversation import Conversation
from network.communication.conversation_manager import ConversationManager
from network.communication.message import Message

moderator = Moderator("../prompts/system_prompt_1/moderator.json")
reviewer1 = Reviewer("../prompts/system_prompt_1/reviewer_1.json")
reviewer2 = Reviewer("../prompts/system_prompt_1/reviewer_2.json")
reviewer3 = Reviewer("../prompts/system_prompt_1/reviewer_3.json")
reviewer4 = Reviewer("../prompts/system_prompt_1/reviewer_4.json")
reviewers = [reviewer1, reviewer2, reviewer3, reviewer4]

feedback_agent = AgentBase("../prompts/system_prompt_1/feedback_agent.json")

conversation = Conversation(moderator, reviewers, feedback_agent)

conversation_manager = ConversationManager(conversation)

#response_message = Message("test_1", "test i am writing something In RESPONSE tO: reviewer_1 to test the new feature CAPS TEST")
#conversation.add_message(response_message)

#response_message1 = Message("test_2", "test i am writing something in response to: reviewer_3 to test the new feature CAPS TEST")
#conversation.add_message(response_message1)

#conversation_manager.get_conversational_rag().clear_all_data()

conversation_manager.simulate_conversation("""
/*CHANGE REQUEST TASK: BUG FIX -http://code.google.com/p/android/issues/detail?id=955Fixed AlertDialog.Builder setMultiChoiceItems losing checked state for invisible items in UI
when backed by a Cursor. Please refer to the issue tracker for more details.*/

//Synthetic comment -- diff --git a/core/java/com/android/internal/app/AlertController.java b/core/java/com/android/internal/app/AlertController.java
//Synthetic comment -- index 53b9654..2b54706 100644

//Synthetic comment -- @@ -784,6 +784,9 @@
<<BEGINNING SNIPPET 1>>>
Cursor cursor) {
CheckedTextView text = (CheckedTextView) view.findViewById(R.id.text1);
text.setText(cursor.getString(cursor.getColumnIndexOrThrow(mLabelColumn)));
}

@Override

<<END SNIPPET 1>>>

//Synthetic comment -- @@ -792,9 +795,6 @@
<<BEGINNING SNIPPET 2>>>
View view = mInflater.inflate(
R.layout.select_dialog_multichoice, parent, false);
bindView(view, context, cursor);
                            if (cursor.getInt(cursor.getColumnIndexOrThrow(mIsCheckedColumn)) == 1) {
                                listView.setItemChecked(cursor.getPosition(), true);
                            }
return view;
}
<<END SNIPPET 2>>>
""")

#rag_content = conversation_manager.get_conversational_rag().retrieve_full_history(str(int(conversation_manager.get_conversation_id())-1))
#print(f"test {rag_content}")