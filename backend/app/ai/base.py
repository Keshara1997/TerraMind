from abc import ABC, abstractmethod


class AIProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        instructions: str,
        prompt: str,
    ) -> str:
        raise NotImplementedError