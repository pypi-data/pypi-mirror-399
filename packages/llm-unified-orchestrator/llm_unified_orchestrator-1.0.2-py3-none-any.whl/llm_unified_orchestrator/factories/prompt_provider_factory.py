from llm_unified_orchestrator.core.prompts.base import PromptProvider
from llm_unified_orchestrator.mlflow.mlflow_config import MlFlowConfig
from llm_unified_orchestrator.mlflow.prompts.prompt_provider import PromptProviderMlFlow

class PromptProviderFactory:
    
    def __init__(self, mlflow_uri: str):
        self.mlflow_uri = mlflow_uri

    def create_mlflow_prompt_provider(self) -> PromptProvider:
        return PromptProviderMlFlow(MlFlowConfig(tracking_host = self.mlflow_uri))