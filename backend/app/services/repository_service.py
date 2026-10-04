import hashlib

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

    def _calculate_file_hash(self, file_path):

        sha256 = hashlib.sha256()

        with open(
            file_path,
            "rb",
        ) as file:

            for block in iter(
                lambda: file.read(1024 * 1024),
                b"",
            ):

                sha256.update(block)

        return sha256.hexdigest()

    def clone_from_github(self, github_url: str):

        repo_name = (
            github_url
            .rstrip("/")
            .split("/")[-1]
        )

        destination = (
            settings.REPOSITORY_DIR
            / repo_name
        )

        settings.REPOSITORY_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not destination.exists():

            logger.info(
                f"Cloning {github_url}"
            )

            Repo.clone_from(
                github_url,
                destination,
            )

        else:

            logger.info(
                "Repository already exists."
            )

        files = self.scanner.scan_repository(
            destination
        )

        parsed_files = 0
        skipped_files = 0
        failed_files = 0
        total_chunks = 0

        for file in files:

            file_path = str(file)

            try:

                current_hash = (
                    self._calculate_file_hash(file)
                )

                stored_hash = (
                    self.chroma.get_file_hash(
                        file_path
                    )
                )

                # File has already been indexed
                # and has not changed.
                if (
                    stored_hash is not None
                    and stored_hash == current_hash
                ):

                    logger.info(
                        f"Skipping unchanged file: "
                        f"{file.name}"
                    )

                    skipped_files += 1

                    continue

                logger.info(
                    f"Parsing : {file.name}"
                )

                parsed = self.parser.parse_file(
                    file
                )

                chunks = (
                    self.chunk_service.chunk_file(
                        parsed
                    )
                )

                if not chunks:

                    logger.info(
                        f"No chunks created: "
                        f"{file.name}"
                    )

                    skipped_files += 1

                    continue

                logger.info(
                    f"Preparing {len(chunks)} "
                    f"chunks for {file.name}"
                )

                # ------------------------------------------------
                # IMPORTANT:
                # Generate ALL embeddings first.
                # We do not delete the old vectors yet.
                # ------------------------------------------------

                prepared_chunks = []

                for index, chunk in enumerate(chunks):

                    logger.info(
                        f"Embedding Chunk "
                        f"{index + 1}/{len(chunks)} : "
                        f"{chunk.file_name}"
                    )

                    embedding = (
                        self.embedding_service
                        .generate_embedding(
                            chunk.content
                        )
                    )

                    prepared_chunks.append(
                        (
                            chunk,
                            embedding,
                        )
                    )

                    logger.info(
                        "Embedding Done"
                    )

                # ------------------------------------------------
                # All embeddings succeeded.
                #
                # Now remove old vectors and store
                # the new version.
                # ------------------------------------------------

                if stored_hash is not None:

                    self.chroma.delete_file(
                        file_path
                    )

                new_chunk_ids = []

                try:

                    for chunk, embedding in prepared_chunks:

                        self.chroma.add_chunk(
                            chunk,
                            embedding,
                            file_hash=current_hash,
                        )

                        new_chunk_ids.append(
                            chunk.chunk_id
                        )

                except Exception:

                    logger.exception(
                        f"Failed storing new chunks "
                        f"for {file.name}"
                    )

                    # Remove partially stored
                    # new chunks.
                    self.chroma.delete_chunks(
                        new_chunk_ids
                    )

                    raise

                parsed_files += 1

                total_chunks += len(
                    prepared_chunks
                )

                logger.info(
                    f"Successfully indexed: "
                    f"{file.name}"
                )

            except Exception as exc:

                failed_files += 1

                logger.exception(
                    f"Failed processing "
                    f"{file.name}: {exc}"
                )

                # Continue with the next file.
                continue

        total_vectors = self.chroma.count()

        logger.info(
            f"Files Parsed : {parsed_files}"
        )

        logger.info(
            f"Files Skipped : {skipped_files}"
        )

        logger.info(
            f"Files Failed : {failed_files}"
        )

        logger.info(
            f"Chunks Created : {total_chunks}"
        )

        logger.info(
            f"Vectors Stored : {total_vectors}"
        )

        status = (
            "success"
            if failed_files == 0
            else "partial_success"
        )

        return {
            "status": status,
            "repository": str(destination),
            "total_files": parsed_files,
            "skipped_files": skipped_files,
            "failed_files": failed_files,
            "total_chunks": total_chunks,
            "vectors": total_vectors,
        }