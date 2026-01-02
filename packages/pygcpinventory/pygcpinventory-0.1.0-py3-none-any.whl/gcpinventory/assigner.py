"""
Object ID assignment system for GCP objects.

Handles stable, unique ID generation for discovered GCP resources.
Simplified from original minietl for core functionality only.
"""

import logging
from typing import Dict, List, Optional, Union

from .models import ETLObject, ObjectType

logger = logging.getLogger(__name__)


class ObjectIDAssigner:
    """Assigns stable, unique IDs to GCP objects."""

    def __init__(self, start_id: int = 1):
        """
        Initialize assigner.

        Args:
            start_id: Starting ID number (default: 1)
        """
        self.next_id = start_id
        self.assignments: Dict[str, str] = {}  # composite key -> object_id
        self.reverse_assignments: Dict[str, Dict[str, str]] = {}  # object_id -> {name, object_type}

    @staticmethod
    def _make_key(name: str, object_type: Optional[Union[ObjectType, str]]) -> str:
        """
        Build the de-duplicated assignment key.

        Names across different object types can collide (e.g., trigger + function
        with the same name), so we namespace the key by type.

        Args:
            name: Object name
            object_type: Object type (ObjectType enum or string)

        Returns:
            Composite key in format "TYPE::name"
        """
        if isinstance(object_type, ObjectType):
            type_value = object_type.value
        elif object_type:
            type_value = str(object_type)
        else:
            return name
        return f"{type_value}::{name}"

    def _record_assignment(self, key: str, obj_id: str, obj: ETLObject) -> None:
        """
        Persist assignment metadata in both forward and reverse caches.

        Args:
            key: Composite key (TYPE::name)
            obj_id: Object ID (e.g., OBJ0001)
            obj: ETLObject instance
        """
        self.assignments[key] = obj_id
        self.reverse_assignments[obj_id] = {
            "name": obj.name,
            "object_type": (
                obj.object_type.value
                if isinstance(obj.object_type, ObjectType)
                else str(obj.object_type)
            ),
        }

    def get_next_id(self) -> str:
        """
        Generate next object ID in format OBJ0001, OBJ0002, etc.

        Returns:
            Object ID string
        """
        obj_id = f"OBJ{self.next_id:04d}"
        self.next_id += 1
        return obj_id

    def assign_object(self, obj: ETLObject) -> str:
        """
        Assign ID to a single ETL object.

        Args:
            obj: ETLObject instance (modified in place)

        Returns:
            Assigned object ID
        """
        # Skip if already has an ID
        if obj.object_id is not None:
            return obj.object_id

        key = self._make_key(obj.name, obj.object_type)

        # Check if we've seen this object before (deduplication)
        if key in self.assignments:
            obj_id = self.assignments[key]
            obj.object_id = obj_id
            return obj_id

        # Generate new ID
        obj_id = self.get_next_id()
        obj.object_id = obj_id

        # Record assignment
        self._record_assignment(key, obj_id, obj)

        logger.debug(f"Assigned {obj_id} to {obj.object_type.value}: {obj.name}")
        return obj_id

    def assign_ids(self, objects: List[ETLObject]) -> None:
        """
        Assign IDs to all objects in the list (modifies in place).

        Args:
            objects: List of ETLObject instances to assign IDs to
        """
        logger.info(f"Assigning IDs to {len(objects)} objects...")

        for obj in objects:
            self.assign_object(obj)

        logger.info(f"✓ Assigned IDs to {len(objects)} objects")

    def get_assignment(
        self,
        name: str,
        object_type: Optional[Union[ObjectType, str]] = None,
    ) -> Optional[str]:
        """
        Get assigned ID for an object by name and type.

        Args:
            name: Object name
            object_type: Object type (optional)

        Returns:
            Object ID if found, None otherwise
        """
        if object_type is not None:
            key = self._make_key(name, object_type)
            return self.assignments.get(key)
        return None

    def get_name(self, object_id: str) -> Optional[str]:
        """
        Get object name from ID.

        Args:
            object_id: Object ID (e.g., OBJ0001)

        Returns:
            Object name if found, None otherwise
        """
        entry = self.reverse_assignments.get(object_id)
        if entry:
            return entry.get("name")
        return None
