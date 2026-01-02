from typing import Type
from pydantic import BaseModel
from llm_unified_orchestrator.core.prompts.base import PromptProvider
from llm_unified_orchestrator.core.task import TaskStatus, WorkflowTask, WorkflowTaskTemplate
from llm_unified_orchestrator.core.workflow import Workflow
from llm_unified_orchestrator.executors.task_finalizer import StepFinalizer
from llm_unified_orchestrator.inference_api.llm_config import LlmConfig
from llm_unified_orchestrator.inference_api.strategies.base import LLMProviderStrategy
from llm_unified_orchestrator.inference_api.strategies.strategy_factory import create_inference_strategy_local

class WorkflowExecutor:
    
    def __init__(self, llm_config: LlmConfig, prompt_provider: PromptProvider, task_finlizaer: StepFinalizer):
        self.llm_config = llm_config
        self.prompt_provider=prompt_provider
        self.finalizer=task_finlizaer
    
    def get_system_prompt(self, workflowTaskTemplate: WorkflowTaskTemplate) -> str:
        if workflowTaskTemplate.system_prompt_id is None:
            return workflowTaskTemplate.system_prompt_default
        
        return self.prompt_provider.get_prompt(workflowTaskTemplate.system_prompt_id)
    
    def get_user_prompt(self, workflowTaskTemplate: WorkflowTaskTemplate, **kwargs) -> str:
        if workflowTaskTemplate.user_prompt_id is None:
            return workflowTaskTemplate.user_prompt_default.format(**kwargs)
        
        return self.prompt_provider.get_prompt(workflowTaskTemplate.user_prompt_id, **kwargs)
    
    def get_model_class(self, module_name: str, class_name:str) -> Type[BaseModel]:
        module = __import__(module_name)
        cls = getattr(module, class_name)
        return cls

    def execute_workflow(self, workflow: Workflow, **kwargs):
        previous = None
        
        for task in workflow.tasks:
            if task.status is TaskStatus.COMPLETED:
                continue
            
            llm_inference = create_inference_strategy_local(name = task.template.strategy, llm_config=self.llm_config) # type: ignore
            self.execute_task(previous=previous, task=task, llm_inference=llm_inference, **kwargs)
            self.finalizer.finalize(task, workflow)

            previous = task
            
    def execute_task(self, previous: WorkflowTask | None, task: WorkflowTask, llm_inference: LLMProviderStrategy, **kwargs):
        system_prompt = self.create_system_prompt(previous, task)
            
        result = llm_inference.inference(
                model=task.template.model,  # type: ignore
                prompt=self.get_user_prompt(task.template, **kwargs), # type: ignore
                system=system_prompt, 
                json_response_type=self.get_model_class(task.result_module_name, task.result_class_name))
        
        task.result = result.model_dump_json()

    def create_system_prompt(self, previous: WorkflowTask | None, task: WorkflowTask):
        system_prompt = self.get_system_prompt(task.template) # type: ignore
        
        if previous is not None:
            if previous.result is None:
                raise ValueError("The previous task did not have results")
            
            task.context = {
                "PreviousTask": f"{previous.template.name}_{previous.template.description}", # type: ignore
                "PreviousTask_Result": previous.result
            }
            
            system_prompt = f"""{system_prompt}
            
            ## Context
            If relevant, use the following information:
            {task.context}"""
            
        return system_prompt