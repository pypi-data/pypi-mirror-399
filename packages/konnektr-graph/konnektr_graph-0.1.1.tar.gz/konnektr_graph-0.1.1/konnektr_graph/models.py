# konnektr_graph/models.py
"""
Konnektr Graph SDK models (Azure-free).
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class ImportJob:
    """Represents an import job."""

    id: str
    status: (
        str  # notstarted, running, completed, diffing, failed, cancelling, cancelled
    )
    input_blob_uri: str
    output_blob_uri: str
    created_date_time: str
    last_action_date_time: Optional[str] = None
    finished_date_time: Optional[str] = None
    purge_date_time: Optional[str] = None
    error: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImportJob":
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
    """Represents a delete job."""

    id: str
    status: str  # notstarted, running, completed, failed, cancelling, cancelled
    created_date_time: str
    last_action_date_time: Optional[str] = None
    finished_date_time: Optional[str] = None
    purge_date_time: Optional[str] = None
    error: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeleteJob":
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
    """Represents a DTDL model."""

    id: str
    description: Optional[Union[str, Dict[str, str]]] = None
    display_name: Optional[Union[str, Dict[str, str]]] = None
    decommissioned: bool = False
    upload_time: Optional[str] = None
    model: Optional[Dict[str, Any]] = None  # The full DTDL definition

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DigitalTwinsModelData":
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
    """Represents an incoming relationship."""

    relationship_id: str
    source_id: str
    relationship_name: str
    relationship_link: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IncomingRelationship":
        return cls(
            relationship_id=data["relationshipId"],
            source_id=data["sourceId"],
            relationship_name=data["relationshipName"],
            relationship_link=data.get("relationshipLink"),
        )


class PagedResult:
    """
    Generic class for paged results.
    Mimics Azure's ItemPaged to some extent but simpler.
    """

    def __init__(self, items: List[Any], next_link: Optional[str] = None):
        self.value = items
        self.next_link = next_link

    @classmethod
    def from_dict(cls, data: Dict[str, Any], item_cls=None) -> "PagedResult":
        items_data = data.get("value", [])
        if item_cls and hasattr(item_cls, "from_dict"):
            items = [item_cls.from_dict(item) for item in items_data]
        else:
            items = items_data
        next_link = data.get("nextLink")
        return cls(items, next_link)


# Type alias for query results which are just dicts usually
QueryResult = PagedResult
