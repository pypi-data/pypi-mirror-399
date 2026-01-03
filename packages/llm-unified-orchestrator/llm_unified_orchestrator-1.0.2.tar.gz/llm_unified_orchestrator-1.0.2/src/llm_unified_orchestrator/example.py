from pydantic import BaseModel, Field
from llm_unified_orchestrator.factories.prompt_provider_factory import PromptProviderFactory
from llm_unified_orchestrator.factories.task_finalizer_factory import TaskFinalizerFactory
from llm_unified_orchestrator.data_store.repository import MongoWorkflowRepository
from llm_unified_orchestrator.executors.generic_executor import WorkflowExecutor
from llm_unified_orchestrator.inference_api.llm_config import LlmConfig
from llm_unified_orchestrator.core.task import WorkflowTask, WorkflowTaskTemplate, TaskStatus
from llm_unified_orchestrator.core.workflow import Workflow, WorkflowStatus

class ResultSummary(BaseModel):
    summary: str = Field(
        description=(
            "The summary of the text"
        )
    )
class ResultSummaryEnriched(BaseModel):
    summary: str = Field(
        description=(
            "The summary of the text"
        )
    )
    enriched_summary: str = Field(
        description=(
            "The enriched summary"
        )
    )

def build_example_workflow(template_summarize: WorkflowTaskTemplate, template_enrich: WorkflowTaskTemplate, template_summarize_context: WorkflowTaskTemplate) -> Workflow:

    task_summarize = WorkflowTask(
        result_module_name="__main__",
        result_class_name=ResultSummary.__name__,
        template_name=template_summarize.name,
        template=template_summarize,
        status=TaskStatus.PENDING,
        result=None,
    )
    
    task_enrich = WorkflowTask(
        result_module_name="__main__",
        result_class_name=ResultSummaryEnriched.__name__,
        template=template_enrich,
        template_name=template_enrich.name,
        status=TaskStatus.PENDING,
        result=None,
    )
    
    task_summarize_final = WorkflowTask(
        result_module_name="__main__",
        result_class_name=ResultSummary.__name__,
        template_name=template_summarize_context.name,
        template=template_summarize_context,
        status=TaskStatus.PENDING,
        result=None,
    )

    workflow = Workflow(
        priority=1,
        name="example_ollama_llama3_workflow",
        description="Example workflow demonstrating Ollama and Llama3.2 tasks",
        tasks=[task_summarize, task_enrich, task_summarize_final],
        status=WorkflowStatus.PENDING
    )

    return workflow


def main() -> None:
    # Dependencies
    repo = MongoWorkflowRepository()
    prompt_factory = PromptProviderFactory(mlflow_uri="http://localhost:5000")
    prompt_provider = prompt_factory.create_mlflow_prompt_provider()
    finalizer_factory = TaskFinalizerFactory(workflow_repository=repo)
    finalizer = finalizer_factory.create()

    llm_config = LlmConfig()
    
    # Generic Workflow Executor
    executor = WorkflowExecutor(llm_config=llm_config, prompt_provider=prompt_provider, task_finlizaer=finalizer)
    
    # Create templates
    ## Summarize text
    template_summarize = WorkflowTaskTemplate(
        description="Call Ollama for initial summarization",
        name="llama3_summary",
        user_prompt_id=None,
        system_prompt_id=None,
        user_prompt_default="Summarize the following: '{text}'",
        system_prompt_default="You are a concise summarizer.",
        strategy="ollama",
        model="llama3.2",
        mcp_tools=None,
    )
    
    ## Enrich the summarized text
    template_enrich = WorkflowTaskTemplate(
        description="Call Llama3.2 for enrichment",
        name="llama3_enrich",
        user_prompt_id=None,
        system_prompt_id=None,
        user_prompt_default="Enrich the summary. Original text: {text}",
        system_prompt_default="You are an assistant that expands ideas.",
        strategy="ollama",
        model="llama3.2",
        mcp_tools=None,
    )
    
    ## Summarize everything
    template_summarize_context = WorkflowTaskTemplate(
        description="Call Ollama for initial summarization",
        name="llama3_context_summary",
        user_prompt_id=None,
        system_prompt_id=None,
        user_prompt_default="Summarize the context using all enrichments",
        system_prompt_default="You are a concise summarizer.",
        strategy="ollama",
        model="llama3.2",
        mcp_tools=None,
    )
    
    # Add the templates to the repository
    repo.update_template(template_summarize)
    repo.update_template(template_enrich)
    repo.update_template(template_summarize_context)

    # Build the workflow using the templates
    workflow = build_example_workflow(template_enrich=template_enrich, template_summarize=template_summarize, template_summarize_context=template_summarize_context)
    try:
        saved = repo.update_workflow(workflow)
        print(f"Saved workflow '{workflow.name}': {saved}")
        
        # The text to summarize and enrich
        kwargs = {'text': 'The essence of software engineering is similar to the detachment of an analyst'}
        
        # Start the workflow
        executor.execute_workflow(workflow=workflow, **kwargs)
        print(f"The final result is: {workflow.tasks.pop().result}")
    except Exception as e:
        print(f"Failed to save workflow: {e}")
    finally:
        repo.close()


if __name__ == "__main__":
    main()
