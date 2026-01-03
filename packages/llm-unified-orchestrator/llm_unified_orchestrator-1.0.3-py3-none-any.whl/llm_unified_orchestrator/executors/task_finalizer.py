from abc import ABC, abstractmethod

from llm_unified_orchestrator.core.task import TaskStatus, WorkflowTask
from llm_unified_orchestrator.core.workflow import Workflow, WorkflowStatus
from llm_unified_orchestrator.data_store.repository import WorkflowRepository


class Finalizer(ABC):
    @abstractmethod
    def finalize_task(self, completed_task: WorkflowTask, workflow: Workflow ):
        pass
    
    @abstractmethod
    def finalize_workflow(self, workflow: Workflow):
        pass
    
    
class PersistentStepFinalizer(Finalizer):
    def __init__(self, workflow_repository: WorkflowRepository):
        self.workflow_repository = workflow_repository
    
    def finalize_task(self, completed_task: WorkflowTask, workflow: Workflow):
        completed_task.status = TaskStatus.COMPLETED
        success = self.workflow_repository.update_workflow(workflow=workflow)
        
        if not success:
            raise ValueError(f"Updating task failed. Workflow: {workflow.name}, task: {completed_task.template_name} ")
    
    def finalize_workflow(self, workflow: Workflow):
        workflow.status = WorkflowStatus.COMPLETED
        success = self.workflow_repository.update_workflow(workflow=workflow)
        
        if not success:
            raise ValueError(f"Updating task failed. Workflow: {workflow.name}, workflow: {workflow.name} ")
            