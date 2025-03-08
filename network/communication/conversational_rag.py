import os
from pinecone import Pinecone
from network.config import pinecone_key

class ConversationalRAG:
    def __init__(self, endpoint):
        self.endpoint = endpoint

        self.pc = Pinecone(api_key=pinecone_key)
        self.index = self.pc.Index("crane")

    def save_iteration(self, conversation, iteration, full_history):
        self.index.upsert(vectors=[(f"{conversation}-{iteration}", [], {
            "history": full_history,
            "iteration": iteration,
            "cr_id": conversation
        })])