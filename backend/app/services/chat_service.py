from google import genai

from app.core.config import settings
from app.services.embedding_service import EmbeddingService
from app.vectorstore.chroma_service import ChromaService


class ChatService:

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.embedding = EmbeddingService()

        self.chroma = ChromaService()

    def ask(self, question: str):

        query_embedding = self.embedding.generate_embedding(
            question
        )

        results = self.chroma.collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        context = ""

        for document in results["documents"][0]:

            context += document
            context += "\n\n-----------------\n\n"

        prompt = f"""
You are RepoPilot AI.

You are an expert software engineer.

Answer ONLY using the repository context below.

If the answer is not found, say:

"I couldn't find that information in the repository."

Repository Context:

{context}

Question:

{question}
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return {
            "answer": response.text,
            "sources": results["metadatas"][0],
        }