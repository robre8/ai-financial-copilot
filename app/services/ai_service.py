from abc import ABC, abstractmethod

class AIService(ABC):

    @abstractmethod
    def ask(self, question: str) -> str:
        pass
