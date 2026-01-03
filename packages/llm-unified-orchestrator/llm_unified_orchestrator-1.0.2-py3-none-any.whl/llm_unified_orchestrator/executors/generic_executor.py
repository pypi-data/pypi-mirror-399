from typing import Type
from pydantic import BaseModel
from llm_unified_orchestrator.core.prompts.base import PromptProvider
from llm_unified_orchestrator.core.task import TaskStatus, WorkflowTask, WorkflowTaskTemplate
from llm_unified_orchestrator.core.workflow import Workflow
from llm_unified_orchestrator.executors.task_finalizer import Finalizer
from llm_unified_orchestrator.inference_api.llm_config import LlmConfig
from llm_unified_orchestrator.inference_api.strategies.base import LLMProviderStrategy
from llm_unified_orchestrator.inference_api.strategies.strategy_factory import create_inference_strategy_local

class WorkflowExecutor:
    
    def __init__(self, llm_config: LlmConfig, prompt_provider: PromptProvider, task_finlizaer: Finalizer):
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
        
        for index, task in enumerate(workflow.tasks):
            if task.status is TaskStatus.COMPLETED:
                continue
            
            llm_inference = create_inference_strategy_local(name = task.template.strategy, llm_config=self.llm_config) # type: ignore
            self.execute_task(task_index=index, previous=previous, task=task, llm_inference=llm_inference, **kwargs)
            self.finalizer.finalize_task(task, workflow)

            previous = task
            
        self.finalizer.finalize_workflow(workflow=workflow)
            
    def execute_task(self, task_index: int, previous: WorkflowTask | None, task: WorkflowTask, llm_inference: LLMProviderStrategy, **kwargs):
        if task.template is None:
            raise ValueError("The template is not set for the task. Template name: " + task.template_name)
        
        system_prompt = self.create_system_prompt(previous_task=previous, task=task, task_index=task_index)
        user_prompt = self.get_user_prompt(task.template, **kwargs)
        
        task.template.system_prompt_default = system_prompt
        task.template.user_prompt_default = user_prompt
            
        result = llm_inference.inference(
                model=task.template.model,  
                prompt= user_prompt,
                system=system_prompt, 
                json_response_type=self.get_model_class(task.result_module_name, task.result_class_name))
        
        task.result = result.model_dump_json()

    def create_system_prompt(self, previous_task: WorkflowTask | None, task: WorkflowTask, task_index: int):
        if task.template is None:
            raise ValueError("The template is not set for the task. Template name: " + task.template_name)
        
        system_prompt = self.get_system_prompt(task.template)
        
        if previous_task is not None:
            if previous_task.result is None:
                raise ValueError("The previous task did not have results")
            
            if previous_task.template is None:
                raise ValueError("The template is not set for the task. Template name: " + previous_task.template_name)
            
            task.context = previous_task.context.copy()
            
            key = f"PreviousTask_{task_index}_{previous_task.template.name.replace(' ', '')}"
            task.context.update({f"{key}_name": f"{previous_task.template.name}"})
            task.context.update({f"{key}_desription": f"{previous_task.template.description}"})
            task.context.update({f"{key}_result": previous_task.result})
            
            system_prompt = f"""{system_prompt}
            
            ## Context
            If relevant, use the following contextual information:
            {task.context}"""
            
        return system_prompt