import uuid

from app.schemas.code_chunk import CodeChunk
from app.schemas.code_file import CodeFile


class ChunkService:

    CHUNK_SIZE = 100

    def chunk_file(self, file: CodeFile):

        chunks = []

        lines = file.content.splitlines()

        for start in range(0, len(lines), self.CHUNK_SIZE):

            end = min(start + self.CHUNK_SIZE, len(lines))

            chunk = "\n".join(lines[start:end])

            chunks.append(

                CodeChunk(

                    chunk_id=str(uuid.uuid4()),

                    file_name=file.file_name,

                    file_path=file.file_path,

                    language=file.language,

                    start_line=start + 1,

                    end_line=end,

                    content=chunk,

                )

            )

        return chunks