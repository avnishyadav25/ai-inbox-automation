import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from core.config import settings
from utils.logger import logger
import os


class VectorStore:
    """Vector store for RAG-based reply generation"""

    def __init__(self):
        os.makedirs(settings.vector_store_path, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=settings.vector_store_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        self.collection = self.client.get_or_create_collection(
            name="email_responses", metadata={"hnsw:space": "cosine"}
        )

        self.encoder = SentenceTransformer(settings.embedding_model)
        logger.info("Vector store initialized")

    def add_email_pair(
        self, email_id: str, incoming_text: str, response_text: str, metadata: Dict = None
    ):
        """Store an email-response pair for future reference"""
        try:
            embedding = self.encoder.encode(incoming_text).tolist()

            self.collection.add(
                ids=[email_id],
                embeddings=[embedding],
                documents=[response_text],
                metadatas=[metadata or {}],
            )

            logger.info(f"Added email pair to vector store: {email_id}")

        except Exception as e:
            logger.error(f"Error adding to vector store: {e}")

    def search_similar_responses(
        self, query_text: str, n_results: int = 3
    ) -> List[Dict]:
        """Search for similar past email responses"""
        try:
            query_embedding = self.encoder.encode(query_text).tolist()

            results = self.collection.query(
                query_embeddings=[query_embedding], n_results=n_results
            )

            similar_responses = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    similar_responses.append(
                        {
                            "response": doc,
                            "distance": results["distances"][0][i]
                            if results.get("distances")
                            else None,
                            "metadata": results["metadatas"][0][i]
                            if results.get("metadatas")
                            else {},
                        }
                    )

            return similar_responses

        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []

    def get_collection_size(self) -> int:
        """Get the number of items in the collection"""
        return self.collection.count()


# Global vector store instance
vector_store = VectorStore()
