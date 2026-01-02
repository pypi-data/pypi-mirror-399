"""
Tests for minietl_core.assigner (ObjectIDAssigner)

TDD: These tests are written FIRST and should FAIL until assigner.py is implemented by Codex.
"""

import pytest
from gcpinventory.models import ETLObject, ObjectType
from gcpinventory.assigner import ObjectIDAssigner


class TestObjectIDAssigner:
    """Test ObjectIDAssigner for stable ID generation"""

    def test_assign_ids_to_objects(self):
        """Test assigning IDs to a list of objects"""
        assigner = ObjectIDAssigner()
        objects = [
            ETLObject(object_id=None, object_type=ObjectType.TRIGGER, name="scheduler-1"),
            ETLObject(object_id=None, object_type=ObjectType.WORKFLOW, name="workflow-1"),
            ETLObject(object_id=None, object_type=ObjectType.FUNCTION, name="function-1"),
        ]

        assigner.assign_ids(objects)

        # All objects should now have IDs
        assert objects[0].object_id == "OBJ0001"
        assert objects[1].object_id == "OBJ0002"
        assert objects[2].object_id == "OBJ0003"

    def test_stable_ids_on_rerun(self):
        """Test that same objects get same IDs across runs"""
        # First run
        assigner1 = ObjectIDAssigner()
        objects1 = [
            ETLObject(object_id=None, object_type=ObjectType.TRIGGER, name="scheduler-1"),
            ETLObject(object_id=None, object_type=ObjectType.WORKFLOW, name="workflow-1"),
        ]
        assigner1.assign_ids(objects1)

        # Second run with same objects
        assigner2 = ObjectIDAssigner()
        objects2 = [
            ETLObject(object_id=None, object_type=ObjectType.TRIGGER, name="scheduler-1"),
            ETLObject(object_id=None, object_type=ObjectType.WORKFLOW, name="workflow-1"),
        ]
        assigner2.assign_ids(objects2)

        # IDs should be stable (same input → same output)
        assert objects1[0].object_id == objects2[0].object_id
        assert objects1[1].object_id == objects2[1].object_id

    def test_assignment_key_format(self):
        """Test that assignment keys follow the expected format"""
        assigner = ObjectIDAssigner()

        # Test internal key generation
        key1 = assigner._make_key("scheduler-1", ObjectType.TRIGGER)
        key2 = assigner._make_key("workflow-1", ObjectType.WORKFLOW)

        assert key1 == "TRIGGER::scheduler-1"
        assert key2 == "WORKFLOW::workflow-1"

    def test_next_id_increments(self):
        """Test that object IDs increment properly"""
        assigner = ObjectIDAssigner()

        id1 = assigner.get_next_id()
        id2 = assigner.get_next_id()
        id3 = assigner.get_next_id()

        assert id1 == "OBJ0001"
        assert id2 == "OBJ0002"
        assert id3 == "OBJ0003"

    def test_skip_already_assigned(self):
        """Test that objects with existing IDs are not reassigned"""
        assigner = ObjectIDAssigner()
        objects = [
            ETLObject(object_id="CUSTOM001", object_type=ObjectType.TRIGGER, name="scheduler-1"),
            ETLObject(object_id=None, object_type=ObjectType.WORKFLOW, name="workflow-1"),
        ]

        assigner.assign_ids(objects)

        # First object should keep its existing ID
        assert objects[0].object_id == "CUSTOM001"
        # Second object should get a new ID
        assert objects[1].object_id == "OBJ0001"

    def test_deduplication(self):
        """Test that duplicate objects get the same ID"""
        assigner = ObjectIDAssigner()
        objects = [
            ETLObject(object_id=None, object_type=ObjectType.TRIGGER, name="scheduler-1"),
            ETLObject(object_id=None, object_type=ObjectType.TRIGGER, name="scheduler-1"),  # Duplicate
            ETLObject(object_id=None, object_type=ObjectType.WORKFLOW, name="workflow-1"),
        ]

        assigner.assign_ids(objects)

        # Duplicates should get the same ID
        assert objects[0].object_id == objects[1].object_id
        # Different object should get different ID
        assert objects[2].object_id != objects[0].object_id

    def test_reverse_assignments_tracking(self):
        """Test that reverse assignments are tracked"""
        assigner = ObjectIDAssigner()
        objects = [
            ETLObject(object_id=None, object_type=ObjectType.TRIGGER, name="scheduler-1"),
        ]

        assigner.assign_ids(objects)

        # Check reverse mapping exists
        assert "OBJ0001" in assigner.reverse_assignments
        assert assigner.reverse_assignments["OBJ0001"]["name"] == "scheduler-1"
        assert assigner.reverse_assignments["OBJ0001"]["object_type"] == "TRIGGER"

    def test_empty_list(self):
        """Test handling of empty object list"""
        assigner = ObjectIDAssigner()
        objects = []

        assigner.assign_ids(objects)  # Should not raise exception

        assert len(objects) == 0
        assert assigner.next_id == 1  # Counter should not increment
