from pydantic import BaseModel


class CodeFile(BaseModel):
    file_name: str
    file_path: str
    language: str
    size: int
    line_count: int
    content: str

    imports: list[str] = []
    classes: list[str] = []
    functions: list[str] = []