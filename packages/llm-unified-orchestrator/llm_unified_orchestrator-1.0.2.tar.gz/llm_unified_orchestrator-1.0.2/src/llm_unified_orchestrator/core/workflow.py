from enum import Enum
from typing import List
from pydantic import BaseModel, Field

from llm_unified_orchestrator.core.task import WorkflowTask


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    

class Workflow(BaseModel):
        name: str = Field(description="Workflow identifier")
        description: str = Field(description="Description of what the workflow does")
        priority: int = Field(0,description="Priority of the task; higher numbers indicate higher priority",)
        tasks: List[WorkflowTask] = Field(description="List of tasks to")
        status: WorkflowStatus = Field(WorkflowStatus.PENDING, description="Current status of the workflow",
)