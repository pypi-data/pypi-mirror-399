from abc import ABC, abstractmethod

from tenacity import retry, stop_after_attempt, wait_exponential


class PromptProvider(ABC):
    @retry(
        wait=wait_exponential(multiplier=4, min=3, max=36),
        stop=stop_after_attempt(5))
    @abstractmethod
    def get_prompt(self, prompt_id: str, **kwargs) -> str:
        pass
