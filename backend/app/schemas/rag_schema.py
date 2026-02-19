from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    answer: str
    model: str
    chunks: list[str]
    chunk_count: int
    context: str

class DebugPromptRequest(BaseModel):
    prompt: str