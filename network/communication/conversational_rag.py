import os
import openai
from pinecone import Pinecone
from network.config import pinecone_key
from network.utils.error_logger import ErrorLogger

class ConversationalRAG:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.pc = Pinecone(api_key=pinecone_key)
        self.index = self.pc.Index("crane")

        index_stats = self.index.describe_index_stats()
        self.error_logger = ErrorLogger()

    def get_embedding(self, text: str) -> list[float]:
        """
        Generate an embedding vector for the given text using OpenAI's
        'text-embedding-ada-002' model.

        Parameters:
            text (str): The input string to be embedded.

        Returns:
            List[float]: A list of floats representing the embedding vector.
        """
        response = openai.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding

    def save_iteration(self, conversation: str, iteration: str, full_history: str) -> int:
        """
        Save a single iteration of a conversation to a Pinecone vector index.

        Parameters:
            conversation (str): A unique identifier for the conversation.
            iteration (int): The current iteration number within the conversation.
            full_history (str): The summary of the conversation history up to this point.

        Returns:
            int: 1 if the operation was successful, 0 if an exception occurred.
        """
        try:
            vector = [0.1] * 1536  # Dummy vector for now

            response = self.index.upsert(vectors=[(f"{conversation}-{iteration}", vector, {
                "history": full_history,
                "iteration": iteration,
                "conversation_id": conversation
            })])

            return 1

        except Exception as e:
            self.error_logger.add_error(f"Exception while saving to RAG (iteration_id={iteration}): {str(e)}")
            return 0

    def clear_all_data(self):
        """
        Delete all vectors from the connected Pinecone index.

        This operation irreversibly removes all stored data, including all
        conversation embeddings and associated metadata.

        Use with caution, especially in production environments.
        """
        self.index.delete(delete_all=True)  # This will delete all vectors in the index

    def retrieve_full_history(self, conversation_id: str):
        """
        Retrieve all stored conversation iterations associated with a given conversation ID.

        Parameters:
            conversation_id (str): The unique identifier for the conversation.

        Returns:
            List[str] or None: A list of conversation history entries in reverse chronological
            order if successful, or None if an exception occurs.
        """
        try:
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
            retrieved_messages = [
                match["metadata"]["history"]
                for match in query_result.get("matches", [])
                if "metadata" in match and "history" in match["metadata"]
            ]

            retrieved_messages.reverse()
            return retrieved_messages

        except Exception as e:
            self.error_logger.add_error(f"Error: Exception occurred while retrieving history for conversation_id={conversation_id}: {str(e)}")
            return None
