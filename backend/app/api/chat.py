from fastapi import APIRouter

from app.schemas.chat_request import ChatRequest
from app.services.chat_service import ChatService


router = APIRouter()

chat_service = ChatService()


@router.post("/ask")
def ask(request: ChatRequest):

    return chat_service.ask(request.question)