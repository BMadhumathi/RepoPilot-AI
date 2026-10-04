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

    def exists(self, file_path: str):

        result = self.collection.get(
            where={
                "file_path": file_path
            },
            include=[
                "metadatas"
            ],
        )

        return len(result["ids"]) > 0

    def get_file_hash(self, file_path: str):

        result = self.collection.get(
            where={
                "file_path": file_path
            },
            include=[
                "metadatas"
            ],
        )

        if not result["ids"]:
            return None

        metadata = result["metadatas"][0]

        return metadata.get("file_hash")

    def delete_file(self, file_path: str):

        logger.info(
            f"Deleting existing vectors for: {file_path}"
        )

        self.collection.delete(
            where={
                "file_path": file_path
            }
        )

    def delete_chunks(self, chunk_ids: list[str]):

        if not chunk_ids:
            return

        self.collection.delete(
            ids=chunk_ids
        )

    def add_chunk(
        self,
        chunk,
        embedding,
        file_hash: str | None = None,
    ):

        metadata = {
            "file_name": chunk.file_name,
            "file_path": chunk.file_path,
            "language": chunk.language,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
        }

        if file_hash is not None:
            metadata["file_hash"] = file_hash

        self.collection.add(
            ids=[
                chunk.chunk_id
            ],
            embeddings=[
                embedding
            ],
            documents=[
                chunk.content
            ],
            metadatas=[
                metadata
            ],
        )

    def query(
        self,
        embedding,
        n_results: int = 5,
    ):

        total = self.collection.count()

        if total == 0:
            return {
                "ids": [[]],
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
            }

        n_results = min(
            n_results,
            total,
        )

        return self.collection.query(
            query_embeddings=[
                embedding
            ],
            n_results=n_results,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

    def count(self):

        logger.info("Counting vectors")

        return self.collection.count()