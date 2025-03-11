import os
import openai
from pinecone import Pinecone
from network.config import pinecone_key

class ConversationalRAG:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.pc = Pinecone(api_key=pinecone_key)
        self.index = self.pc.Index("crane")

        index_stats = self.index.describe_index_stats()
        #print(f"[DEBUG] Full Index Stats: {index_stats}")

    def get_embedding(self, text):
        """Generate text embeddings using OpenAI"""
        response = openai.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding

    def save_iteration(self, conversation, iteration, full_history):
        """Save a conversation iteration into Pinecone"""
        vector = [0.1] * 1536  # Dummy vector for now

        #print(f"\n[SAVE] Storing conversation_id={conversation}, Iteration={iteration}")
        #print(f"[SAVE] Full history:\n{full_history}\n")

        response = self.index.upsert(vectors=[(f"{conversation}-{iteration}", vector, {
            "history": full_history,
            "iteration": iteration,
            "conversation_id": conversation
        })])

        #print(f"\n[SAVE] Pinecone Upsert Response: {response}\n")

        # Debug: Check if data is stored
        stats = self.index.describe_index_stats()
        #print(f"[SAVE] Index Stats After Upsert: {stats}\n")

    def clear_all_data(self):
        """Clear all data in Pinecone Index"""
        #print("[CLEAR] Deleting all vectors in Pinecone index")
        self.index.delete(delete_all=True)  # This will delete all vectors in the index

    def retrieve_full_history(self, conversation_id):
        """Retrieve all stored iterations for a given conversation ID (conversation_id)."""
        #print(f"[RETRIEVE] Querying stored messages for conversation_id={conversation_id}.")

        # Use a dummy vector for retrieval (same size as stored vectors)
        query_vector = [0.1] * 1536

        # Query Pinecone with metadata filtering
        query_result = self.index.query(
            vector=query_vector,
            top_k=10,  # Retrieve multiple matches
            include_metadata=True,
            namespace="",  # Explicitly set default namespace
            filter={"conversation_id": {"$eq": str(conversation_id)}}
        )

        #print(f"[RAW QUERY RESULTS] {query_result}")

        # Extract stored messages only for the matching conversation_id
        retrieved_messages = [
            match["metadata"]["history"]
            for match in query_result.get("matches", [])
            if "metadata" in match and "history" in match["metadata"]
        ]

        retrieved_messages.reverse()

        #print(f"[FINAL RETRIEVED MESSAGES] {retrieved_messages}")
        return retrieved_messages
