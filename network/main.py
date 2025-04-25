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

conversation_manager.simulate_conversation("""/* CR_TASK Change Request:

Modify the BankAccount class to introduce a new feature: Adding a checkBalance method, which will allow checking the balance without synchronization.

Ensure that the withdrawal operation can fail after a certain threshold, say if the balance is below a certain limit (e.g., $50).

Add a log message when the account's balance goes below $50 during any operation. */""",
                                           """class BankAccount {
    private int balance = 0;

    // Synchronized method to ensure thread safety
    public synchronized void deposit(int amount) {
        balance += amount;
        System.out.println("Deposited: " + amount + ", New Balance: " + balance);
    }

    // Synchronized method to ensure thread safety
    public synchronized void withdraw(int amount) {
        if (balance >= amount) {
            balance -= amount;
            System.out.println("Withdrew: " + amount + ", New Balance: " + balance);
        } else {
            System.out.println("Insufficient funds to withdraw: " + amount);
        }
    }

    public int getBalance() {
        return balance;
    }
}

public class BankTest {
    public static void main(String[] args) {
        BankAccount account = new BankAccount();

        // Thread for depositing money
        Thread depositThread = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                account.deposit(100);
                try { Thread.sleep(100); } catch (InterruptedException e) { e.printStackTrace(); }
            }
        });

        // Thread for withdrawing money
        Thread withdrawThread = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                account.withdraw(50);
                try { Thread.sleep(150); } catch (InterruptedException e) { e.printStackTrace(); }
            }
        });

        depositThread.start();
        withdrawThread.start();
    }
}
""")

#rag_content = conversation_manager.get_conversational_rag().retrieve_full_history(str(int(conversation_manager.get_conversation_id())-1))
#print(f"test {rag_content}")