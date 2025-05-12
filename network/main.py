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

conversation_manager = ConversationManager(conversation)

#response_message = Message("test_1", "test i am writing something In RESPONSE tO: reviewer_1 to test the new feature CAPS TEST")
#conversation.add_message(response_message)

#response_message1 = Message("test_2", "test i am writing something in response to: reviewer_3 to test the new feature CAPS TEST")
#conversation.add_message(response_message1)

#conversation_manager.get_conversational_rag().clear_all_data()

conversation_manager.simulate_conversation("""/* CR_TASK Fix the Multi-page SMS sending error to several receipents\n\nChange-Id:Iefde94b638413e3c1761f17c3065b20a044e5958Signed-off-by: Sang-Jun Park <sj2202.park@samsung.com>*/""",
                                           """//<Beginning of snippet n. 0>

old mode 100644
new mode 100755

protected boolean mStorageAvailable = true;
protected boolean mReportMemoryStatusPending = false;

protected static int getNextConcatenatedRef() {
sConcatenatedRef += 1;
return sConcatenatedRef;

if (sentIntent != null) {
try {
                    sentIntent.send(Activity.RESULT_OK);
} catch (CanceledException ex) {}
}
} else {
if (ar.result != null) {
fillIn.putExtra("errorCode", ((SmsResponse)ar.result).errorCode);
}
                    tracker.mSentIntent.send(mContext, error, fillIn);

} catch (CanceledException ex) {}
}
}

//<End of snippet n. 0>""")

#rag_content = conversation_manager.get_conversational_rag().retrieve_full_history(str(int(conversation_manager.get_conversation_id())-1))
#print(f"test {rag_content}")