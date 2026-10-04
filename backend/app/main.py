from fastapi import FastAPI

from app.api.repository import router as repository_router
from app.api.chat import router as chat_router
from app.api.agent import router as agent_router


app = FastAPI()


app.include_router(
    repository_router
)

app.include_router(
    chat_router
)

app.include_router(
    agent_router
)


@app.get("/")
def home():

    return {
        "status": "working"
    }