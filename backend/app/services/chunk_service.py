import hashlib

from app.schemas.code_chunk import CodeChunk


class ChunkService:

    def __init__(self, chunk_size: int = 100, overlap: int = 20):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_file(self, code_file) -> list[CodeChunk]:

        lines = code_file.content.splitlines()

        if not lines:
            return []

        chunks = []

        start = 0

        while start < len(lines):

            end = min(
                start + self.chunk_size,
                len(lines),
            )

            chunk_content = "\n".join(lines[start:end])

            # Create a deterministic ID based on
            # the file + line range + content.
            chunk_id_source = (
                f"{code_file.file_path}:"
                f"{start + 1}:"
                f"{end}:"
                f"{chunk_content}"
            )

            chunk_id = hashlib.sha256(
                chunk_id_source.encode("utf-8")
            ).hexdigest()

            chunks.append(
                CodeChunk(
                    chunk_id=chunk_id,
                    file_name=code_file.file_name,
                    file_path=code_file.file_path,
                    language=code_file.language,
                    start_line=start + 1,
                    end_line=end,
                    content=chunk_content,
                )
            )

            if end >= len(lines):
                break

            start = end - self.overlap

        return chunks