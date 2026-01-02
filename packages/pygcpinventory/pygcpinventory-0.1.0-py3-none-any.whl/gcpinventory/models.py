"""
Data models for minietl-core

Defines core data structures for GCP object metadata collection.
Simplified from original minietl to focus on metadata-only operations.
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from enum import Enum


class ObjectType(str, Enum):
    """Enumeration of GCP object types for metadata collection."""

    TRIGGER = "TRIGGER"  # Cloud Scheduler jobs
    WORKFLOW = "WORKFLOW"  # Cloud Workflows
    FUNCTION = "FUNCTION"  # Cloud Functions
    DATASET = "DATASET"  # BigQuery datasets (renamed from BQDATASET)
    BUCKET = "BUCKET"  # Cloud Storage buckets (renamed from GCS_BUCKET)
    TOPIC = "TOPIC"  # Pub/Sub topics (renamed from PUBSUB)
    SINK = "SINK"  # Logging sinks


class EdgeType(str, Enum):
    """Enumeration of relationship types between objects."""

    INVOKES = "invokes"  # A triggers/calls B
    TRIGGERS = "triggers"  # A triggers B
    WRITES_TO = "writes_to"  # A writes to B
    READS_FROM = "reads_from"  # A reads from B
    DEPENDS_ON = "depends_on"  # A depends on B
    CONTAINS = "contains"  # A contains B


class ObjectStatus(str, Enum):
    """Enumeration of object status values."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    INACTIVE = "inactive"


@dataclass
class ETLObject:
    """
    Represents a GCP object discovered during inventory collection.

    Tracks metadata for GCP resources across services.
    """

    object_id: str  # Unique identifier (OBJ001, OBJ002, ...)
    object_type: ObjectType  # Type of GCP object
    name: str  # Name of the object
    parent_id: Optional[str] = None  # Reference to parent object
    gcp_resource_name: Optional[str] = None  # Full GCP resource name
    description: Optional[str] = None  # Description of the object
    effective_start: Optional[str] = None  # SCD2: When this version became active
    effective_end: Optional[str] = None  # SCD2: When this version was superseded
    version: int = 1  # SCD2: Version number
    status: ObjectStatus = ObjectStatus.ACTIVE  # Current status
    created_at: Optional[str] = None  # Creation timestamp
    updated_at: Optional[str] = None  # Last update timestamp
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata (JSON)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        d = asdict(self)
        d["object_type"] = self.object_type.value
        d["status"] = self.status.value
        if self.metadata is None:
            d["metadata"] = {}
        return d


@dataclass
class ETLEdge:
    """
    Represents a relationship between two GCP objects.

    Captures dependencies and data flows in the infrastructure.
    """

    edge_id: str  # Unique edge identifier
    source_object_id: str  # Source object ID
    target_object_id: str  # Target object ID
    edge_type: EdgeType  # Type of relationship
    source_name: Optional[str] = None  # Cached source name
    target_name: Optional[str] = None  # Cached target name
    method: Optional[str] = None  # How they interact (HTTP POST, etc.)
    is_active: bool = True  # Whether this edge is currently active
    created_at: Optional[str] = None  # Creation timestamp

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        d = asdict(self)
        d["edge_type"] = self.edge_type.value
        return d
