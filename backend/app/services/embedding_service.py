import time

from google import genai
from google.api_core.exceptions import ResourceExhausted

from app.core.config import settings
from app.core.logger import logger


class EmbeddingService:

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.model = "gemini-embedding-001"

        self.max_retries = 4

    def generate_embedding(self, text: str):

        if not text or not text.strip():
            raise ValueError(
                "Cannot generate embedding for empty text."
            )

        for attempt in range(self.max_retries + 1):

            try:

                response = self.client.models.embed_content(
                    model=self.model,
                    contents=text,
                )

                return response.embeddings[0].values

            except ResourceExhausted:

                if attempt >= self.max_retries:

                    logger.error(
                        "Gemini embedding rate limit persisted "
                        f"after {self.max_retries} retries."
                    )

                    raise

                delay = 2 ** attempt

                logger.warning(
                    "Gemini 429 rate limit. "
                    f"Retrying in {delay} seconds "
                    f"(attempt {attempt + 1}/"
                    f"{self.max_retries})"
                )

                time.sleep(delay)