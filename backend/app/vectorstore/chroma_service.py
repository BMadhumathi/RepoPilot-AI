import chromadb

from app.core.config import settings
from app.core.logger import logger


class ChromaService:

    def __init__(self):

        logger.info("Initializing Chroma Client")

        self.client = chromadb.PersistentClient(
            path=str(settings.CHROMA_DB)
        )

        logger.info("Getting Collection")

        self.collection = self.client.get_or_create_collection(
            name="repo_chunks"
        )

        logger.info("Chroma Ready")

    def exists(self, file_path):

        result = self.collection.get(
            where={
                "file_path": file_path
            }
        )

        return len(result["ids"]) > 0
    
    def search(self, embedding, k=5):

        result = self.collection.query(
            query_embeddings=[embedding],
            n_results=k,
        )

        return result
    def add_chunk(
        self,
        chunk,
        embedding,
    ):

        logger.info("Before collection.add()")

        self.collection.add(
            ids=[chunk.chunk_id],
            embeddings=[embedding],
            documents=[chunk.content],
            metadatas=[
                {
                    "file_name": chunk.file_name,
                    "file_path": chunk.file_path,
                    "language": chunk.language,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                }
            ],
        )

        logger.info("After collection.add()")

    def count(self):

        logger.info("Counting vectors")

        return self.collection.count()