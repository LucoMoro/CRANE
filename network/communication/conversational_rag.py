import os
from pinecone import Pinecone
from network.config import pinecone_key

class ConversationalRAG:
    def __init__(self, endpoint):
        self.endpoint = endpoint

        self.pc = Pinecone(api_key=pinecone_key)
        self.index = self.pc.Index("crane")

    def save_iteration(self, conversation, iteration, full_history):
        vector = [0.1] * 1536 #needed since upsert expects to have a vector of dimension 1536
        self.index.upsert(vectors=[(f"{conversation}-{iteration}", vector, {
            "history": full_history,
            "iteration": iteration,
            "cr_id": conversation
        })])