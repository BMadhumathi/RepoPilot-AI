import time

from google import genai
from google.api_core.exceptions import ResourceExhausted

from app.core.config import settings


class EmbeddingService:

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def generate_embedding(self, text: str):

        while True:

            try:

                response = self.client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=text,
                )

                return response.embeddings[0].values

            except ResourceExhausted:

                print("429 Rate Limit. Waiting 30 seconds...")

                time.sleep(30)