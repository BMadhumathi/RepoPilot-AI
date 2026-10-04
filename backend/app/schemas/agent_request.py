from pydantic import BaseModel


class AgentRequest(BaseModel):

    repository_name: str

    question: str