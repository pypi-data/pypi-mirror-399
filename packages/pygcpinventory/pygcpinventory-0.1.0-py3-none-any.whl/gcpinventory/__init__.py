"""
gcpinventory: GCP Project Inventory Collection Library

A lightweight library for collecting GCP object metadata across services.
"""

from .version import __version__
from .models import ETLObject, ObjectType, EdgeType, ObjectStatus, ETLEdge
from .assigner import ObjectIDAssigner

__all__ = [
    "__version__",
    "ETLObject",
    "ObjectType",
    "EdgeType",
    "ObjectStatus",
    "ETLEdge",
    "ObjectIDAssigner",
]
