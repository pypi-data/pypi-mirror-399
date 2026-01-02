"""
Tests for minietl_core.models

Following TDD: These tests are written FIRST and should FAIL until models.py is implemented.
"""

import pytest
from gcpinventory.models import ETLObject, ObjectType, EdgeType, ObjectStatus


class TestObjectType:
    """Test ObjectType enum"""

    def test_object_type_values(self):
        """Test that ObjectType enum has correct values"""
        assert ObjectType.TRIGGER.value == "TRIGGER"
        assert ObjectType.WORKFLOW.value == "WORKFLOW"
        assert ObjectType.FUNCTION.value == "FUNCTION"
        assert ObjectType.DATASET.value == "DATASET"
        assert ObjectType.BUCKET.value == "BUCKET"
        assert ObjectType.TOPIC.value == "TOPIC"
        assert ObjectType.SINK.value == "SINK"

    def test_object_type_count(self):
        """Test that we have exactly 7 object types"""
        assert len(list(ObjectType)) == 7


class TestEdgeType:
    """Test EdgeType enum"""

    def test_edge_type_values(self):
        """Test that EdgeType enum has correct values"""
        assert EdgeType.INVOKES.value == "invokes"
        assert EdgeType.TRIGGERS.value == "triggers"
        assert EdgeType.WRITES_TO.value == "writes_to"
        assert EdgeType.READS_FROM.value == "reads_from"
        assert EdgeType.DEPENDS_ON.value == "depends_on"
        assert EdgeType.CONTAINS.value == "contains"

    def test_edge_type_count(self):
        """Test that we have exactly 6 edge types"""
        assert len(list(EdgeType)) == 6


class TestObjectStatus:
    """Test ObjectStatus enum"""

    def test_object_status_values(self):
        """Test that ObjectStatus enum has correct values"""
        assert ObjectStatus.ACTIVE.value == "active"
        assert ObjectStatus.ARCHIVED.value == "archived"
        assert ObjectStatus.DELETED.value == "deleted"
        assert ObjectStatus.INACTIVE.value == "inactive"


class TestETLObject:
    """Test ETLObject dataclass"""

    def test_create_minimal_object(self):
        """Test creating ETLObject with minimal required fields"""
        obj = ETLObject(
            object_id="OBJ001",
            object_type=ObjectType.TRIGGER,
            name="test-scheduler"
        )
        assert obj.object_id == "OBJ001"
        assert obj.object_type == ObjectType.TRIGGER
        assert obj.name == "test-scheduler"
        assert obj.status == ObjectStatus.ACTIVE  # Default value

    def test_create_full_object(self):
        """Test creating ETLObject with all fields"""
        obj = ETLObject(
            object_id="OBJ002",
            object_type=ObjectType.WORKFLOW,
            name="etl-workflow",
            parent_id="OBJ001",
            gcp_resource_name="projects/test/locations/us-central1/workflows/etl-workflow",
            description="Test workflow",
            effective_start="2025-01-01T00:00:00Z",
            effective_end=None,
            version=1,
            status=ObjectStatus.ACTIVE,
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
            metadata={"key": "value"}
        )
        assert obj.object_id == "OBJ002"
        assert obj.parent_id == "OBJ001"
        assert obj.metadata == {"key": "value"}

    def test_to_dict(self):
        """Test converting ETLObject to dictionary"""
        obj = ETLObject(
            object_id="OBJ003",
            object_type=ObjectType.FUNCTION,
            name="transform-func",
            metadata={"runtime": "python39"}
        )
        d = obj.to_dict()

        assert isinstance(d, dict)
        assert d["object_id"] == "OBJ003"
        assert d["object_type"] == "FUNCTION"  # Should be string value
        assert d["name"] == "transform-func"
        assert d["metadata"] == {"runtime": "python39"}

    def test_to_dict_with_none_metadata(self):
        """Test to_dict with None metadata (should return empty dict)"""
        obj = ETLObject(
            object_id="OBJ004",
            object_type=ObjectType.DATASET,
            name="analytics",
            metadata=None
        )
        d = obj.to_dict()
        assert d["metadata"] == {}  # None should convert to empty dict


class TestETLEdge:
    """Test ETLEdge dataclass"""

    def test_create_edge(self):
        """Test creating ETLEdge"""
        from gcpinventory.models import ETLEdge

        edge = ETLEdge(
            edge_id="edge001",
            source_object_id="OBJ001",
            target_object_id="OBJ002",
            edge_type=EdgeType.TRIGGERS
        )
        assert edge.edge_id == "edge001"
        assert edge.source_object_id == "OBJ001"
        assert edge.target_object_id == "OBJ002"
        assert edge.edge_type == EdgeType.TRIGGERS
        assert edge.is_active is True  # Default value

    def test_edge_to_dict(self):
        """Test converting ETLEdge to dictionary"""
        from gcpinventory.models import ETLEdge

        edge = ETLEdge(
            edge_id="edge002",
            source_object_id="OBJ002",
            target_object_id="OBJ003",
            edge_type=EdgeType.WRITES_TO,
            source_name="workflow-1",
            target_name="dataset-1",
            method="HTTP POST"
        )
        d = edge.to_dict()

        assert isinstance(d, dict)
        assert d["edge_id"] == "edge002"
        assert d["edge_type"] == "writes_to"  # Should be string value
        assert d["method"] == "HTTP POST"
