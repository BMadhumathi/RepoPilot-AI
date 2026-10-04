from fastapi import APIRouter, HTTPException

from app.agents.code_agents import CodeAgent
from app.schemas.agent_request import AgentRequest


router = APIRouter()

code_agent = CodeAgent()


@router.post("/agent")
def run_code_agent(
    request: AgentRequest,
):

    try:

        return code_agent.ask(
            question=request.question,
            repository_name=request.repository_name,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )