from llm_unified_orchestrator.data_store.repository import WorkflowRepository
from llm_unified_orchestrator.executors.task_finalizer import PersistentStepFinalizer, StepFinalizer

class TaskFinalizerFactory:

    def __init__(self, workflow_repository: WorkflowRepository ):
        self.workflow_repository = workflow_repository

    def create(self) -> StepFinalizer:
        return PersistentStepFinalizer(workflow_repository=self.workflow_repository)