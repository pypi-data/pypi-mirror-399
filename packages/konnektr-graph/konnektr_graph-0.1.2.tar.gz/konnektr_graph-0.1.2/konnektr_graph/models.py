# konnektr_graph/models.py
"""
Konnektr Graph SDK models (Azure-free).
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class ImportJob:
    """
    Represents an import job.

    Attributes:
        id: The unique identifier for the job.
        status: The current status of the job (e.g., 'notstarted', 'running', 'completed').
        input_blob_uri: The URI of the input blob.
        output_blob_uri: The URI of the output blob.
        created_date_time: The date and time the job was created.
        last_action_date_time: The date and time of the last action.
        finished_date_time: The date and time the job finished.
        purge_date_time: The date and time the job will be purged.
        error: Optional error information if the job failed.
    """

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImportJob":
        """
        Create an ImportJob instance from a dictionary.

        Args:
            data: A dictionary containing the import job data.

        Returns:
            An ImportJob instance.
        """
        return cls(
            id=data["id"],
            status=data["status"],
            input_blob_uri=data["inputBlobUri"],
            output_blob_uri=data["outputBlobUri"],
            created_date_time=data["createdDateTime"],
            last_action_date_time=data.get("lastActionDateTime"),
            finished_date_time=data.get("finishedDateTime"),
            purge_date_time=data.get("purgeDateTime"),
            error=data.get("error"),
        )


@dataclass
class DeleteJob:
    """
    Represents a delete job.

    Attributes:
        id: The unique identifier for the job.
        status: The current status of the job (e.g., 'notstarted', 'running', 'completed').
        created_date_time: The date and time the job was created.
        last_action_date_time: The date and time of the last action.
        finished_date_time: The date and time the job finished.
        purge_date_time: The date and time the job will be purged.
        error: Optional error information if the job failed.
    """

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeleteJob":
        """
        Create a DeleteJob instance from a dictionary.

        Args:
            data: A dictionary containing the delete job data.

        Returns:
            A DeleteJob instance.
        """
        return cls(
            id=data["id"],
            status=data["status"],
            created_date_time=data["createdDateTime"],
            last_action_date_time=data.get("lastActionDateTime"),
            finished_date_time=data.get("finishedDateTime"),
            purge_date_time=data.get("purgeDateTime"),
            error=data.get("error"),
        )


@dataclass
class DigitalTwinsModelData:
    """
    Represents a DTDL model metadata and definition.

    Attributes:
        id: The unique identifier for the model.
        description: Optional description of the model.
        display_name: Optional display name of the model.
        decommissioned: Whether the model is decommissioned.
        upload_time: The date and time the model was uploaded.
        model: The full DTDL model definition.
    """

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DigitalTwinsModelData":
        """
        Create a DigitalTwinsModelData instance from a dictionary.

        Args:
            data: A dictionary containing the model data.

        Returns:
            A DigitalTwinsModelData instance.
        """
        return cls(
            id=data["id"],
            description=data.get("description"),
            display_name=data.get("displayName"),
            decommissioned=data.get("decommissioned", False),
            upload_time=data.get("uploadTime"),
            model=data.get("model"),
        )


@dataclass
class IncomingRelationship:
    """
    Represents an incoming relationship for a digital twin.

    Attributes:
        relationship_id: The ID of the relationship.
        source_id: The source of the relationship.
        relationship_name: The name of the relationship.
        relationship_link: A link to the relationship definition.
    """

    relationship_id: str
    source_id: str
    relationship_name: str
    relationship_link: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IncomingRelationship":
        """
        Create an IncomingRelationship instance from a dictionary.

        Args:
            data: A dictionary containing the relationship data.

        Returns:
            An IncomingRelationship instance.
        """
        return cls(
            relationship_id=data["relationshipId"],
            source_id=data["sourceId"],
            relationship_name=data["relationshipName"],
            relationship_link=data.get("relationshipLink"),
        )
