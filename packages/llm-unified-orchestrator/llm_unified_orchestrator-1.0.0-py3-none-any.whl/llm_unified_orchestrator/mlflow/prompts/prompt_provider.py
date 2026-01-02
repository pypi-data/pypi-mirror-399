import mlflow
from mlflow import genai

from tenacity import retry, stop_after_attempt, wait_exponential
from llm_unified_orchestrator.core.prompts.base import PromptProvider
from llm_unified_orchestrator.mlflow.mlflow_config import MlFlowConfig


class PromptProviderMlFlow(PromptProvider):
    
    def __init__(self, config: MlFlowConfig ) -> None:
        super().__init__()
        mlflow.set_tracking_uri(config.tracking_host)
        
    @retry(
        wait=wait_exponential(multiplier=4, min=3, max=36),
        stop=stop_after_attempt(5))
    def get_prompt(self, prompt_id: str, **kwargs) -> str:
        return str(genai.load_prompt(f"prompts:/{prompt_id}").format(kwargs=kwargs))