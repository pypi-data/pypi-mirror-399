from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pymongo import MongoClient, errors
from pymongo.collection import Collection
from pydantic import ValidationError

from llm_unified_orchestrator.core.task import WorkflowTaskTemplate
from llm_unified_orchestrator.core.workflow import Workflow

class WorkflowRepository(ABC):
    """
    Repository interface for workflows.
    Implementations must provide these methods to read/update/delete workflows.
    """

    @abstractmethod
    def list_workflows(self) -> List[Workflow]:
        raise NotImplementedError

    @abstractmethod
    def get_workflow(self, name: str) -> Optional[Workflow]:
        raise NotImplementedError

    @abstractmethod
    def update_workflow(self, workflow: Workflow) -> bool:
        raise NotImplementedError

    @abstractmethod
    def delete_workflow(self, name: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError

class MongoWorkflowRepository(WorkflowRepository):
    """
    Simple MongoDB-backed repository for workflows.

    - Expects workflow documents in the configured collection with fields that match the `Workflow` model.
    - `get_workflow`/`list_workflows` return `Workflow` instances.
    - `update_workflow` replaces the stored document (upsert by `name`).
    """

    def __init__(
        self,
        uri: str = "mongodb://localhost:27017",
        db_name: str = "dev",
        collection_name: str = "llm_workflows",
        templates_collection_name: str = "llm_templates",
        *,
        connect_timeout_ms: int = 2000,
    ) -> None:
        self._uri = uri
        self._db_name = db_name
        self._collection_name = collection_name
        self._templates_collection_name = templates_collection_name
        self._client = MongoClient(self._uri, serverSelectionTimeoutMS=connect_timeout_ms)
        self._db = self._client[self._db_name]
        self._collection: Collection = self._db[self._collection_name]
        self._templates_collection: Collection = self._db[self._templates_collection_name]

    def list_workflows(self) -> List[Workflow]:
        """
        Return all workflows from the collection as `Workflow` models.
        """
        try:
            docs = self._collection.find()
            workflows: List[Workflow] = []
            for doc in docs:
                try:
                    workflows.append(Workflow.model_validate(doc))
                except ValidationError:
                    continue
            return workflows
        except errors.PyMongoError as e:
            raise RuntimeError(f"Failed to list workflows: {e}") from e
    
    def update_template(self, template: WorkflowTaskTemplate):
        try:
            doc: Dict[str, Any] = template.model_dump(by_alias=True, exclude_none=True)
            result = self._templates_collection.replace_one({"name": template.name}, doc, upsert=True)
            return bool(result.acknowledged)
        except errors.PyMongoError as e:
            raise RuntimeError(f"Failed to update template '{template.name}': {e}") from e

    def get_workflow(self, name: str) -> Optional[Workflow]:
        """
        Find a workflow by its `name` field and return it as a `Workflow` model, or `None` if not found.
        """
        try:
            doc = self._collection.find_one({"name": name})
            if doc:
                # Load the template from the templates collection if it exists
                template_doc = self._templates_collection.find_one({"name": doc.get("template_name")})
                if template_doc:
                    doc["template"] = WorkflowTaskTemplate.model_validate(template_doc)
            
            if not doc:
                return None
            return Workflow.model_validate(doc)
        except errors.PyMongoError as e:
            raise RuntimeError(f"Failed to fetch workflow '{name}': {e}") from e
        except ValidationError as e:
            raise ValueError(f"Stored workflow '{name}' does not match model: {e}") from e

    def update_workflow(self, workflow: Workflow) -> bool:
        """
        Replace (or insert) the workflow document in MongoDB. Upserts by `name`.

        Returns True if the operation was acknowledged by MongoDB.
        """
        try:
            # Convert pydantic model to dict suitable for storage.
            # exclude_none keeps the document small; include all fields you need to persist.
            doc: Dict[str, Any] = workflow.model_dump(by_alias=True, exclude_none=True)
            # Remove any nested Pydantic private attrs if present
            # Upsert by unique `name` field
            result = self._collection.replace_one({"name": workflow.name}, doc, upsert=True)
            return bool(result.acknowledged)
        except errors.PyMongoError as e:
            raise RuntimeError(f"Failed to update workflow '{workflow.name}': {e}") from e

    def delete_workflow(self, name: str) -> bool:
        """
        Delete a workflow by name. Returns True if deletion was acknowledged.
        """
        try:
            result = self._collection.delete_one({"name": name})
            return bool(result.acknowledged)
        except errors.PyMongoError as e:
            raise RuntimeError(f"Failed to delete workflow '{name}': {e}") from e

    def close(self) -> None:
        """Close the underlying MongoDB connection."""
        try:
            self._client.close()
        except Exception:
            pass