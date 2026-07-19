from pydantic import BaseModel, HttpUrl


class RepositoryRequest(BaseModel):
    github_url: HttpUrl


class RepositoryResponse(BaseModel):
    status: str
    repository: str
    total_files: int
    total_chunks: int