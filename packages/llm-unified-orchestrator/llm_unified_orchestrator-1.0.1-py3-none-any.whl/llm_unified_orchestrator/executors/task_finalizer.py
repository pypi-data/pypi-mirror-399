from abc import ABC, abstractmethod

from llm_unified_orchestrator.core.task import TaskStatus, WorkflowTask
from llm_unified_orchestrator.core.workflow import Workflow
from llm_unified_orchestrator.data_store.repository import WorkflowRepository


class StepFinalizer(ABC):
    @abstractmethod
    def finalize(self, completed_task: WorkflowTask, workflow: Workflow ):
        pass
    
    
class PersistentStepFinalizer(StepFinalizer):
    def __init__(self, workflow_repository: WorkflowRepository):
        self.workflow_repository = workflow_repository
    
    def finalize(self, completed_task, workflow):
        completed_task.status = TaskStatus.COMPLETED
        success = self.workflow_repository.update_workflow(workflow=workflow)
        
        if not success:
            raise ValueError(f"Updating task failed. Workflow: {workflow.name}, task: {completed_task.template_name} ")
            