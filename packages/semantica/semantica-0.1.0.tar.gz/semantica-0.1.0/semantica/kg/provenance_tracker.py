"""
Provenance Tracking Module

This module provides comprehensive source tracking and lineage capabilities
for the Semantica framework, enabling tracking of data origins and evolution
for knowledge graph entities and relationships.

Key Features:
    - Entity provenance tracking (source, timestamp, metadata)
    - Relationship provenance tracking
    - Lineage retrieval (complete provenance history)
    - Source aggregation (multiple sources per entity)
    - Temporal tracking (first seen, last updated)

Main Classes:
    - ProvenanceTracker: Main provenance tracking engine

Example Usage:
    >>> from semantica.kg import ProvenanceTracker
    >>> tracker = ProvenanceTracker()
    >>> tracker.track_entity("entity_1", source="source_1", metadata={"confidence": 0.9})
    >>> lineage = tracker.get_lineage("entity_1")
    >>> sources = tracker.get_all_sources("entity_1")

Author: Semantica Contributors
License: MIT
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker


class ProvenanceTracker:
    """
    Provenance tracking engine.

    This class provides provenance tracking capabilities, maintaining source
    and lineage information for knowledge graph entities and relationships.
    Tracks multiple sources per entity and maintains temporal information.

    Features:
        - Entity and relationship provenance tracking
        - Multiple source support per entity
        - Temporal tracking (first seen, last updated)
        - Metadata storage and aggregation
        - Lineage retrieval

    Example Usage:
        >>> tracker = ProvenanceTracker()
        >>> tracker.track_entity("entity_1", source="source_1", metadata={"confidence": 0.9})
        >>> lineage = tracker.get_lineage("entity_1")
        >>> sources = tracker.get_all_sources("entity_1")
    """

    def __init__(self, **config):
        """
        Initialize provenance tracker.

        Sets up the tracker with configuration and initializes provenance
        data storage.

        Args:
            **config: Configuration options (currently unused)
        """
        self.logger = get_logger("provenance_tracker")
        self.config = config
        self.provenance_data: Dict[str, Any] = {}

        # Initialize progress tracker
        self.progress_tracker = get_progress_tracker()
        # Ensure progress tracker is enabled
        if not self.progress_tracker.enabled:
            self.progress_tracker.enabled = True

        self.logger.debug("Provenance tracker initialized")

    def track_entity(
        self, entity_id: str, source: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Track entity provenance.

        This method records provenance information for an entity, including
        source, timestamp, and optional metadata. Supports multiple sources
        per entity and maintains first seen and last updated timestamps.

        Args:
            entity_id: Entity identifier
            source: Source identifier (e.g., "file_1", "api_endpoint_2")
            metadata: Optional metadata dictionary (e.g., confidence scores,
                     extraction methods, etc.)
        """
        if entity_id not in self.provenance_data:
            self.provenance_data[entity_id] = {
                "sources": [],
                "first_seen": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "metadata": {},
            }

        # Add source tracking
        source_entry = {
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        self.provenance_data[entity_id]["sources"].append(source_entry)
        self.provenance_data[entity_id]["last_updated"] = datetime.now().isoformat()

        # Merge metadata
        if metadata:
            self.provenance_data[entity_id]["metadata"].update(metadata)

        self.logger.debug(
            f"Tracked provenance for entity {entity_id} from source {source}"
        )

    def track_relationship(
        self,
        relationship_id: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Track relationship provenance.

        This method records provenance information for a relationship, including
        source, timestamp, and optional metadata. Similar to track_entity()
        but for relationships.

        Args:
            relationship_id: Relationship identifier
            source: Source identifier
            metadata: Optional metadata dictionary
        """
        if relationship_id not in self.provenance_data:
            self.provenance_data[relationship_id] = {
                "sources": [],
                "first_seen": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "metadata": {},
            }

        source_entry = {
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        self.provenance_data[relationship_id]["sources"].append(source_entry)
        self.provenance_data[relationship_id][
            "last_updated"
        ] = datetime.now().isoformat()

        if metadata:
            self.provenance_data[relationship_id]["metadata"].update(metadata)

    def get_all_sources(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get all sources for an entity.

        This method retrieves all source entries for a given entity, including
        source identifiers, timestamps, and metadata.

        Args:
            entity_id: Entity identifier

        Returns:
            list: List of source entry dictionaries, each containing:
                - source: Source identifier
                - timestamp: ISO format timestamp
                - metadata: Source metadata dictionary
        """
        if entity_id not in self.provenance_data:
            return []

        return self.provenance_data[entity_id].get("sources", [])

    def get_lineage(self, entity_id: str) -> Dict[str, Any]:
        """
        Get complete lineage for an entity.

        This method retrieves complete lineage information for an entity,
        including all sources, temporal information, and aggregated metadata.

        Args:
            entity_id: Entity identifier

        Returns:
            dict: Complete lineage information containing:
                - sources: List of all source entries
                - first_seen: ISO timestamp of first source
                - last_updated: ISO timestamp of most recent source
                - metadata: Aggregated metadata dictionary
        """
        if entity_id not in self.provenance_data:
            return {}

        return self.provenance_data[entity_id].copy()

    def get_provenance(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Get provenance for entity.

        This method is an alias for get_lineage(), returning the complete
        provenance information for an entity, or None if not tracked.

        Args:
            entity_id: Entity identifier

        Returns:
            dict: Complete provenance information (same as get_lineage()),
                  or None if entity is not tracked
        """
        return self.provenance_data.get(entity_id)
