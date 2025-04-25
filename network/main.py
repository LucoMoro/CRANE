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

conversation_manager.simulate_conversation("""/* CR_TASK Fix issue "Permission Denial: broadcasting Intent ... requires null"

The added if corresponds to a similar check on another Permission Denial: broadcasting some pages
above within the same module.

The problem was spotted with broadcasting a ACTION_NEW_OUTGOING_CALL intent which currently does not
require any permissions. It is suggested to require a new permission MAKE_OUTGOING_CALL for the
broadcast receiver in Phone application. */""",
                                           """(ResolveInfo)nextReceiver;

boolean skip = false;
            int perm = checkComponentPermission(info.activityInfo.permission,
                    r.callingPid, r.callingUid,
                    info.activityInfo.exported
                            ? -1 : info.activityInfo.applicationInfo.uid);
            if (perm != PackageManager.PERMISSION_GRANTED) {
                Log.w(TAG, "Permission Denial: broadcasting "
                        + r.intent.toString()
                        + " from " + r.callerPackage + " (pid=" + r.callingPid
                        + ", uid=" + r.callingUid + ")"
                        + " requires " + info.activityInfo.permission
                        + " due to receiver " + info.activityInfo.packageName
                        + "/" + info.activityInfo.name);
                skip = true;
            }
if (r.callingUid != Process.SYSTEM_UID &&
r.requiredPermission != null) {
try {

""")

#rag_content = conversation_manager.get_conversational_rag().retrieve_full_history(str(int(conversation_manager.get_conversation_id())-1))
#print(f"test {rag_content}")