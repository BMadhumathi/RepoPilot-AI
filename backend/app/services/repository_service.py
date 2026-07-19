from git import Repo

from app.core.config import settings
from app.core.logger import logger

from app.services.file_scanner import FileScanner
from app.services.code_parser import CodeParser
from app.services.chunk_service import ChunkService
from app.services.embedding_service import EmbeddingService

from app.vectorstore.chroma_service import ChromaService


class RepositoryService:

    def __init__(self):

        self.scanner = FileScanner()
        self.parser = CodeParser()
        self.chunk_service = ChunkService()
        self.embedding_service = EmbeddingService()
        self.chroma = ChromaService()

    def clone_from_github(self, github_url: str):

        repo_name = github_url.rstrip("/").split("/")[-1]

        destination = settings.REPOSITORY_DIR / repo_name

        settings.REPOSITORY_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not destination.exists():

            logger.info(f"Cloning {github_url}")

            Repo.clone_from(
                github_url,
                destination,
            )

        else:

            logger.info("Repository already exists.")

        files = self.scanner.scan_repository(destination)

        parsed_files = 0
        total_chunks = 0
        skipped_files = 0

        for file in files:

            # Skip files that are already in Chroma
            if self.chroma.exists(str(file)):

                logger.info(f"Skipping : {file.name}")

                skipped_files += 1

                continue

            logger.info(f"Parsing : {file.name}")

            parsed = self.parser.parse_file(file)

            parsed_files += 1

            chunks = self.chunk_service.chunk_file(parsed)

            total_chunks += len(chunks)

            for index, chunk in enumerate(chunks):

                logger.info(
                    f"[{parsed_files}/{len(files)}] "
                    f"Embedding Chunk {index + 1}/{len(chunks)} : {chunk.file_name}"
                )

                embedding = self.embedding_service.generate_embedding(
                    chunk.content
                )

                logger.info("Embedding Done")

                self.chroma.add_chunk(
                    chunk,
                    embedding,
                )

                logger.info("Stored")

        logger.info(f"Files Parsed : {parsed_files}")
        logger.info(f"Files Skipped : {skipped_files}")
        logger.info(f"Chunks Created : {total_chunks}")
        logger.info(f"Vectors Stored : {self.chroma.count()}")

        return {
            "status": "success",
            "repository": str(destination),
            "total_files": parsed_files,
            "skipped_files": skipped_files,
            "total_chunks": total_chunks,
            "vectors": self.chroma.count(),
        }