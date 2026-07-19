from pydantic import BaseModel


class CodeChunk(BaseModel):
    chunk_id: str
    file_name: str
    file_path: str
    language: str

    start_line: int
    end_line: int

    content: str