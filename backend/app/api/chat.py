from fastapi import APIRouter, HTTPException

from app.schemas.chat_request import ChatRequest
from app.services.chat_service import ChatService


router = APIRouter()

chat_service = ChatService()


@router.post("/chat")
def chat(request: ChatRequest):

    try:

        return chat_service.ask(
            request.question
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )