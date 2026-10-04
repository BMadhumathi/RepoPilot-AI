import time

from google import genai
from google.genai import errors

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

        self.model = "gemini-2.5-flash"

        self.top_k = 5

        self.max_retries = 3

    def _generate_answer(self, prompt: str):

        for attempt in range(self.max_retries + 1):

            try:

                return self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )

            except errors.ServerError:

                if attempt >= self.max_retries:
                    raise

                delay = 2 ** attempt

                time.sleep(delay)

    def ask(self, question: str):

        if not question or not question.strip():

            raise ValueError(
                "Question cannot be empty."
            )

        query_embedding = (
            self.embedding.generate_embedding(
                question
            )
        )

        results = self.chroma.query(
            embedding=query_embedding,
            n_results=self.top_k,
        )

        documents = results.get(
            "documents",
            [[]],
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]],
        )[0]

        distances = results.get(
            "distances",
            [[]],
        )[0]

        if not documents:

            return {
                "answer": (
                    "I couldn't find that information "
                    "in the repository."
                ),
                "sources": [],
            }

        context_parts = []

        for index, document in enumerate(documents):

            metadata = (
                metadatas[index]
                if index < len(metadatas)
                else {}
            )

            distance = (
                distances[index]
                if index < len(distances)
                else None
            )

            file_name = metadata.get(
                "file_name",
                "Unknown file",
            )

            file_path = metadata.get(
                "file_path",
                "Unknown path",
            )

            start_line = metadata.get(
                "start_line",
                "?",
            )

            end_line = metadata.get(
                "end_line",
                "?",
            )

            source_number = index + 1

            context_parts.append(
                f"""
[SOURCE {source_number}]
File: {file_name}
Path: {file_path}
Lines: {start_line}-{end_line}
Distance: {distance}

Code:
{document}
"""
            )

        context = "\n\n".join(
            context_parts
        )

        prompt = f"""
You are RepoPilot AI, a software repository
assistant.

Answer the user's question using ONLY the
repository context provided below.

Rules:

1. Do not invent repository facts.

2. Do not use information that is not supported
   by the provided repository context.

3. If the repository context does not contain
   enough information to answer the question,
   say exactly:

"I couldn't find that information in the repository."

4. When making a repository-specific claim,
   cite the relevant source using:

[SOURCE 1]
[SOURCE 2]

etc.

5. When useful, mention the file name and
   relevant line range.

6. Do not claim that you inspected files that
   were not included in the repository context.

Repository Context:

{context}

User Question:

{question}
"""

        response = self._generate_answer(prompt)

        return {
            "answer": response.text,
            "sources": metadatas,
        }