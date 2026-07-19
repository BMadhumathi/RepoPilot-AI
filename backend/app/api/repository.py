from fastapi import APIRouter

from app.schemas.repository import RepositoryRequest, RepositoryResponse
from app.services.repository_service import RepositoryService

router = APIRouter()

repository_service = RepositoryService()


@router.post("/load", response_model=RepositoryResponse)
def load_repository(request: RepositoryRequest):
    return repository_service.clone_from_github(str(request.github_url))