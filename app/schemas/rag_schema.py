from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    answer: str

class DebugPromptRequest(BaseModel):
    prompt: str