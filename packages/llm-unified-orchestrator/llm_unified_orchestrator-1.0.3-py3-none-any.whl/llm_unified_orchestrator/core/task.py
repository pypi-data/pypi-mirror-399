from enum import Enum
from typing import Dict,  Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    
class WorkflowTaskTemplate(BaseModel):
    name: str = Field(description="Unique template name")
    description: str = Field(description="Description of the template")
    user_prompt_default: str = Field(description="User prompt for the model",)
    system_prompt_default: str = Field(description="System prompt for the model",)
    user_prompt_id: Optional[str] = Field(None, description="User prompt identifier for the model",)
    system_prompt_id: Optional[str] = Field(None, description="System prompt identifier for the model",)
    strategy:str = Field(description="Strategy identifier to select an execution strategy",)
    model: str = Field(description="Model identifier to use for inference",)
    mcp_tools: Optional[str] = Field(None,description="List of MCP tool identifiers used during task execution",)        
    
class WorkflowTask(BaseModel):
    status: TaskStatus = Field(TaskStatus.PENDING,description="Current status of the task",)
    context: Dict[str, str] = Field(
        default_factory=dict,
        description="Contextual data to provide additional information for the task",
    )
    result: Optional[str] = Field(None, description="Result produced by the task")
    result_module_name: str = Field(description="The module name of the expected result. Must be pydantic")
    result_class_name: str = Field(description="The class name of the exprected result. Must be pydantic")
    template_name: str = Field(description="A workflow task template identifier")
    template: WorkflowTaskTemplate | None = Field(None, description="A workflow task template")
    latency_ms: float | None = Field(None, description="The latency of the task")
    
    
    


