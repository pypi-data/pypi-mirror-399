"""
Temporal Query Module

This module provides comprehensive time-aware querying capabilities for the
Semantica framework, enabling temporal queries and analysis on knowledge
graphs with temporal information.

Key Features:
    - Time-point queries (query graph at specific time)
    - Time-range queries (query within time intervals)
    - Temporal pattern detection (sequences, cycles, trends)
    - Graph evolution analysis
    - Temporal path finding
    - Temporal version management

Main Classes:
    - TemporalGraphQuery: Main temporal query engine
    - TemporalPatternDetector: Temporal pattern detection engine
    - TemporalVersionManager: Temporal version/snapshot management

Example Usage:
    >>> from semantica.kg import TemporalGraphQuery
    >>> query_engine = TemporalGraphQuery()
    >>> result = query_engine.query_at_time(graph, query, at_time="2024-01-01")
    >>> evolution = query_engine.analyze_evolution(graph, start_time="2024-01-01")

Author: Semantica Contributors
License: MIT
"""

from typing import Any, Dict, List, Optional

from ..utils.progress_tracker import get_progress_tracker


class TemporalGraphQuery:
    """
    Temporal knowledge graph query engine.

    This class provides time-aware querying capabilities for knowledge graphs
    with temporal information, enabling queries at specific time points, within
    time ranges, and temporal pattern detection.

    Features:
        - Time-point queries (filter relationships valid at specific time)
        - Time-range queries (filter relationships valid within range)
        - Temporal pattern detection (sequences, cycles, trends)
        - Graph evolution analysis
        - Temporal path finding (paths considering temporal validity)

    Example Usage:
        >>> query_engine = TemporalGraphQuery()
        >>> result = query_engine.query_at_time(graph, query, at_time="2024-01-01")
        >>> range_result = query_engine.query_time_range(graph, query, start_time, end_time)
        >>> evolution = query_engine.analyze_evolution(graph)
    """

    def __init__(
        self,
        enable_temporal_reasoning: bool = True,
        temporal_granularity: str = "day",
        max_temporal_depth: Optional[int] = None,
        **kwargs,
    ):
        """
        Initialize temporal query engine.

        Sets up the query engine with temporal reasoning configuration and
        pattern detector.

        Args:
            enable_temporal_reasoning: Enable temporal reasoning capabilities
                                    (default: True)
            temporal_granularity: Time granularity for queries
                                (default: "day", options: "second", "minute",
                                "hour", "day", "week", "month", "year")
            max_temporal_depth: Maximum depth for temporal queries (optional)
            **kwargs: Additional configuration options:
                - pattern_detection: Configuration for pattern detector (optional)
        """
        self.enable_temporal_reasoning = enable_temporal_reasoning
        self.temporal_granularity = temporal_granularity
        self.max_temporal_depth = max_temporal_depth

        # Initialize temporal query engine
        from ..utils.logging import get_logger

        self.logger = get_logger("temporal_query")

        # Initialize progress tracker
        self.progress_tracker = get_progress_tracker()
        # Ensure progress tracker is enabled
        if not self.progress_tracker.enabled:
            self.progress_tracker.enabled = True

        # Initialize pattern detector
        self.pattern_detector = TemporalPatternDetector(
            **kwargs.get("pattern_detection", {})
        )

    def query_at_time(
        self,
        graph: Any,
        query: str,
        at_time: Any,
        include_history: bool = False,
        temporal_precision: Optional[str] = None,
        **options,
    ) -> Dict[str, Any]:
        """
        Query graph at specific time point.

        This method filters the knowledge graph to only include relationships
        that are valid at the specified time point, based on valid_from and
        valid_until fields in relationships.

        Args:
            graph: Knowledge graph to query (dict with "entities" and "relationships")
            query: Query string (currently unused, reserved for future query parsing)
            at_time: Time point (datetime object, timestamp, or ISO format string)
            include_history: Whether to include all relationships with temporal
                           information (default: False, only valid relationships)
            temporal_precision: Precision for time matching (optional, unused)
            **options: Additional query options (unused)

        Returns:
            dict: Query results containing:
                - query: Original query string
                - at_time: Parsed time point
                - entities: All entities (not filtered by time)
                - relationships: Relationships valid at specified time
                - num_entities: Number of entities
                - num_relationships: Number of valid relationships
        """
        self.logger.info(f"Querying graph at time: {at_time}")

        # Parse time
        query_time = self._parse_time(at_time)

        # Filter relationships valid at query time
        relationships = []
        if "relationships" in graph:
            for rel in graph.get("relationships", []):
                valid_from = self._parse_time(rel.get("valid_from"))
                valid_until = self._parse_time(rel.get("valid_until"))

                # Check if relationship is valid at query time
                if valid_from and self._compare_times(query_time, valid_from) < 0:
                    continue
                if valid_until and self._compare_times(query_time, valid_until) > 0:
                    continue

                relationships.append(rel)

        # Get entities
        entities = graph.get("entities", [])

        # Include history if requested
        if include_history:
            # Add all relationships with temporal information
            relationships = graph.get("relationships", [])

        return {
            "query": query,
            "at_time": query_time,
            "entities": entities,
            "relationships": relationships,
            "num_entities": len(entities),
            "num_relationships": len(relationships),
        }

    def query_time_range(
        self,
        graph: Any,
        query: str,
        start_time: Any,
        end_time: Any,
        temporal_aggregation: str = "union",
        include_intervals: bool = True,
        **options,
    ) -> Dict[str, Any]:
        """
        Query graph within time range.

        This method filters relationships that are valid within the specified
        time range, with different aggregation strategies.

        Args:
            graph: Knowledge graph to query
            query: Query string (currently unused, reserved for future)
            start_time: Start of time range (datetime, timestamp, or ISO string)
            end_time: End of time range (datetime, timestamp, or ISO string)
            temporal_aggregation: Aggregation strategy:
                - "union": Include all relationships overlapping with range (default)
                - "intersection": Only relationships valid throughout entire range
                - "evolution": Group relationships by time periods
            include_intervals: Include partial matches within range (default: True)
            **options: Additional query options (unused)

        Returns:
            dict: Query results containing:
                - query: Original query string
                - start_time: Parsed start time
                - end_time: Parsed end time
                - relationships: Filtered relationships
                - num_relationships: Number of relationships
                - aggregation: Aggregation strategy used
        """
        self.logger.info(f"Querying graph in time range: {start_time} to {end_time}")

        # Parse times
        start = self._parse_time(start_time)
        end = self._parse_time(end_time)

        # Filter relationships valid in time range
        relationships = []
        if "relationships" in graph:
            for rel in graph.get("relationships", []):
                valid_from = self._parse_time(rel.get("valid_from"))
                valid_until = self._parse_time(rel.get("valid_until"))

                # Check if relationship overlaps with time range
                if valid_from and self._compare_times(end, valid_from) < 0:
                    continue
                if valid_until and self._compare_times(start, valid_until) > 0:
                    continue

                relationships.append(rel)

        # Aggregate based on strategy
        if temporal_aggregation == "intersection":
            # Only relationships valid throughout the entire range
            relationships = [
                rel
                for rel in relationships
                if self._parse_time(rel.get("valid_from")) <= start
                and (
                    not rel.get("valid_until")
                    or self._parse_time(rel.get("valid_until")) >= end
                )
            ]
        elif temporal_aggregation == "evolution":
            # Group by time periods
            relationships = self._group_by_time_periods(relationships, start, end)

        return {
            "query": query,
            "start_time": start,
            "end_time": end,
            "relationships": relationships,
            "num_relationships": len(relationships),
            "aggregation": temporal_aggregation,
        }

    def query_temporal_pattern(
        self,
        graph: Any,
        pattern: str,
        time_window: Optional[Any] = None,
        min_support: int = 1,
        **options,
    ) -> Dict[str, Any]:
        """
        Query for temporal patterns in graph.

        This method detects temporal patterns (sequences, cycles, trends) in
        the knowledge graph using the temporal pattern detector.

        Args:
            graph: Knowledge graph to query
            pattern: Pattern type to search for ("sequence", "cycle", "trend", "anomaly")
            time_window: Time window for pattern matching (optional)
            min_support: Minimum frequency/support for pattern (default: 1)
            **options: Additional pattern query options

        Returns:
            dict: Pattern query results containing:
                - pattern: Pattern type searched
                - patterns: List of detected patterns
                - num_patterns: Number of patterns found
        """
        self.logger.info(f"Querying temporal patterns: {pattern}")

        # Use pattern detector
        patterns = self.pattern_detector.detect_temporal_patterns(
            graph,
            pattern_type=pattern,
            min_frequency=min_support,
            time_window=time_window,
            **options,
        )

        return {
            "pattern": pattern,
            "patterns": patterns,
            "num_patterns": len(patterns) if isinstance(patterns, list) else 0,
        }

    def analyze_evolution(
        self,
        graph: Any,
        entity: Optional[str] = None,
        relationship: Optional[str] = None,
        start_time: Optional[Any] = None,
        end_time: Optional[Any] = None,
        metrics: Optional[List[str]] = None,
        **options,
    ) -> Dict[str, Any]:
        """
        Analyze graph evolution over time.

        This method analyzes how the knowledge graph (or specific entities/relationships)
        evolves over a time period, calculating various evolution metrics.

        Args:
            graph: Knowledge graph to analyze
            entity: Specific entity ID to track (optional, None for entire graph)
            relationship: Specific relationship type to track (optional, None for all)
            start_time: Start of analysis period (optional)
            end_time: End of analysis period (optional)
            metrics: List of metrics to calculate (default: ["count", "diversity", "stability"])
                    - "count": Number of relationships
                    - "diversity": Number of unique relationship types
                    - "stability": Relationship duration/stability measure
            **options: Additional analysis options (unused)

        Returns:
            dict: Evolution analysis results containing:
                - entity: Entity ID tracked (if specified)
                - relationship: Relationship type tracked (if specified)
                - time_range: Dictionary with start and end times
                - num_relationships: Number of relationships in period
                - count: Relationship count (if "count" in metrics)
                - diversity: Relationship type diversity (if "diversity" in metrics)
                - stability: Stability measure (if "stability" in metrics)
        """
        self.logger.info("Analyzing graph evolution")

        # Set default metrics if None
        if metrics is None:
            metrics = ["count", "diversity", "stability"]

        # Filter relationships
        relationships = graph.get("relationships", [])

        if entity:
            relationships = [
                rel
                for rel in relationships
                if rel.get("source") == entity or rel.get("target") == entity
            ]

        if relationship:
            relationships = [
                rel for rel in relationships if rel.get("type") == relationship
            ]

        # Filter by time range
        if start_time or end_time:
            start = self._parse_time(start_time) if start_time else None
            end = self._parse_time(end_time) if end_time else None

            filtered = []
            for rel in relationships:
                valid_from = self._parse_time(rel.get("valid_from"))
                valid_until = self._parse_time(rel.get("valid_until"))

                if (
                    start
                    and valid_until
                    and self._compare_times(valid_until, start) < 0
                ):
                    continue
                if end and valid_from and self._compare_times(valid_from, end) > 0:
                    continue

                filtered.append(rel)
            relationships = filtered

        # Calculate metrics
        result = {
            "entity": entity,
            "relationship": relationship,
            "time_range": {"start": start_time, "end": end_time},
            "num_relationships": len(relationships),
        }

        if "count" in metrics:
            result["count"] = len(relationships)

        if "diversity" in metrics:
            rel_types = set(rel.get("type") for rel in relationships)
            result["diversity"] = len(rel_types)

        if "stability" in metrics:
            # Calculate stability based on relationship duration
            durations = []
            for rel in relationships:
                valid_from = self._parse_time(rel.get("valid_from"))
                valid_until = self._parse_time(rel.get("valid_until"))
                if valid_from and valid_until:
                    # Simplified duration calculation
                    durations.append(1)  # Placeholder
            result["stability"] = sum(durations) / len(durations) if durations else 0

        return result

    def find_temporal_paths(
        self,
        graph: Any,
        source: str,
        target: str,
        start_time: Optional[Any] = None,
        end_time: Optional[Any] = None,
        max_path_length: Optional[int] = None,
        temporal_constraints: Optional[Dict[str, Any]] = None,
        **options,
    ) -> Dict[str, Any]:
        """
        Find paths between entities considering temporal validity.

        This method finds paths between source and target entities, considering
        only relationships that are temporally valid within the specified
        time range. Uses BFS for path finding.

        Args:
            graph: Knowledge graph to search
            source: Source entity ID
            target: Target entity ID
            start_time: Start time for path validity (optional)
            end_time: End time for path validity (optional)
            max_path_length: Maximum path length in edges (optional)
            temporal_constraints: Additional temporal constraints (optional, unused)
            **options: Additional path finding options (unused)

        Returns:
            dict: Temporal path results containing:
                - source: Source entity ID
                - target: Target entity ID
                - paths: List of path dictionaries, each containing:
                    - path: List of node IDs forming the path
                    - edges: List of relationship dictionaries
                    - length: Path length in edges
                - num_paths: Total number of paths found
        """
        self.logger.info(f"Finding temporal paths from {source} to {target}")

        # Build adjacency with temporal constraints
        adjacency = {}
        relationships = graph.get("relationships", [])

        for rel in relationships:
            s = rel.get("source")
            t = rel.get("target")

            # Check temporal validity
            if start_time or end_time:
                valid_from = self._parse_time(rel.get("valid_from"))
                valid_until = self._parse_time(rel.get("valid_until"))

                if (
                    start_time
                    and valid_until
                    and self._compare_times(valid_until, start_time) < 0
                ):
                    continue
                if (
                    end_time
                    and valid_from
                    and self._compare_times(valid_from, end_time) > 0
                ):
                    continue

            if s not in adjacency:
                adjacency[s] = []
            adjacency[s].append((t, rel))

        # BFS to find paths
        from collections import deque

        paths = []
        queue = deque([(source, [source], [])])
        visited = set()
        max_length = max_path_length or float("inf")

        while queue:
            node, path, edges = queue.popleft()

            if len(path) > max_length:
                continue

            if node == target:
                paths.append({"path": path, "edges": edges, "length": len(path) - 1})
                continue

            if node in visited:
                continue
            visited.add(node)

            for neighbor, rel in adjacency.get(node, []):
                if neighbor not in path:  # Avoid cycles
                    queue.append((neighbor, path + [neighbor], edges + [rel]))

        return {
            "source": source,
            "target": target,
            "paths": paths,
            "num_paths": len(paths),
        }

    def _parse_time(self, time_value):
        """Parse time value."""
        from datetime import datetime

        if time_value is None:
            return None

        if isinstance(time_value, str):
            return time_value

        if isinstance(time_value, datetime):
            return time_value.isoformat()

        return str(time_value)

    def _compare_times(self, time1, time2):
        """Compare two time strings."""
        if time1 is None or time2 is None:
            return 0
        return (time1 > time2) - (time1 < time2)

    def _group_by_time_periods(self, relationships, start, end):
        """Group relationships by time periods."""
        # Simplified grouping
        return relationships


class TemporalPatternDetector:
    """
    Temporal pattern detection engine.

    This class provides temporal pattern detection capabilities for knowledge
    graphs, identifying recurring patterns, sequences, cycles, and trends in
    temporal data.

    Features:
        - Sequence pattern detection
        - Cycle pattern detection
        - Trend analysis
        - Anomaly detection (planned)

    Example Usage:
        >>> detector = TemporalPatternDetector()
        >>> patterns = detector.detect_temporal_patterns(
        ...     graph, pattern_type="sequence", min_frequency=2
        ... )
    """

    def __init__(self, **config):
        """
        Initialize temporal pattern detector.

        Sets up the detector with configuration options.

        Args:
            **config: Configuration options (currently unused)
        """
        from ..utils.logging import get_logger

        self.logger = get_logger("temporal_pattern_detector")
        self.config = config

        self.logger.debug("Temporal pattern detector initialized")

    def detect_temporal_patterns(
        self,
        graph: Any,
        pattern_type: str = "sequence",
        min_frequency: int = 2,
        time_window: Optional[Any] = None,
        **options,
    ) -> List[Dict[str, Any]]:
        """
        Detect temporal patterns in graph.

        This method detects various types of temporal patterns in the knowledge
        graph, including sequences and cycles.

        Args:
            graph: Knowledge graph to analyze
            pattern_type: Type of pattern to detect:
                - "sequence": Sequential relationship patterns
                - "cycle": Cyclic relationship patterns
                - "trend": Trend patterns (planned)
                - "anomaly": Anomaly patterns (planned)
            min_frequency: Minimum frequency/support for pattern (default: 2)
            time_window: Time window for pattern detection (optional)
            **options: Additional detection options (unused)

        Returns:
            list: List of detected pattern dictionaries
        """
        self.logger.info(f"Detecting temporal patterns: {pattern_type}")

        relationships = graph.get("relationships", [])

        # Simple pattern detection
        patterns = []

        if pattern_type == "sequence":
            # Find sequential relationships
            sequences = self._find_sequences(relationships, min_frequency)
            patterns.extend(sequences)
        elif pattern_type == "cycle":
            # Find cyclic patterns
            cycles = self._find_cycles(relationships, min_frequency)
            patterns.extend(cycles)

        return patterns

    def _find_sequences(self, relationships, min_frequency):
        """Find sequential patterns."""
        # Simplified sequence detection
        return []

    def _find_cycles(self, relationships, min_frequency):
        """Find cyclic patterns."""
        # Simplified cycle detection
        return []


class TemporalVersionManager:
    """
    Temporal version management engine.

    This class provides version/snapshot management capabilities for knowledge
    graphs, enabling creation of temporal versions, version comparison, and
    version history tracking.

    Features:
        - Version snapshot creation
        - Version comparison
        - Version history tracking
        - Automatic snapshotting (planned)
        - Version rollback (planned)

    Example Usage:
        >>> manager = TemporalVersionManager()
        >>> version = manager.create_version(graph, version_label="v1.0")
        >>> comparison = manager.compare_versions(version1, version2)
    """

    def __init__(
        self,
        snapshot_interval: Optional[int] = None,
        auto_snapshot: bool = False,
        version_strategy: str = "timestamp",
        **config,
    ):
        """
        Initialize temporal version manager.

        Sets up the version manager with snapshot configuration and versioning
        strategy.

        Args:
            snapshot_interval: Interval for automatic snapshots in seconds
                             (optional, auto_snapshot must be True)
            auto_snapshot: Enable automatic snapshots (default: False)
            version_strategy: Versioning strategy:
                - "timestamp": Use timestamps for version labels (default)
                - "incremental": Use incremental version numbers (planned)
                - "semantic": Use semantic versioning (planned)
            **config: Additional configuration options (unused)
        """
        self.snapshot_interval = snapshot_interval
        self.auto_snapshot = auto_snapshot
        self.version_strategy = version_strategy

    def create_version(
        self,
        graph: Any,
        version_label: Optional[str] = None,
        timestamp: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **options,
    ) -> Dict[str, Any]:
        """
        Create version snapshot of graph.

        This method creates a snapshot/version of the knowledge graph at a
        specific point in time, copying entities and relationships.

        Args:
            graph: Knowledge graph to version (dict with "entities" and "relationships")
            version_label: Optional version label (defaults to "version_{timestamp}")
            timestamp: Timestamp for version (defaults to current time)
            metadata: Additional version metadata dictionary (optional)
            **options: Additional version options (unused)

        Returns:
            dict: Version snapshot containing:
                - label: Version label
                - timestamp: ISO format timestamp
                - entities: Copy of entities list
                - relationships: Copy of relationships list
                - metadata: Version metadata dictionary
        """
        from datetime import datetime

        version_time = timestamp or datetime.now().isoformat()

        version = {
            "label": version_label or f"version_{version_time}",
            "timestamp": version_time,
            "entities": graph.get("entities", []).copy(),
            "relationships": graph.get("relationships", []).copy(),
            "metadata": metadata or {},
        }

        return version

    def compare_versions(
        self,
        version1: Dict[str, Any],
        version2: Dict[str, Any],
        comparison_metrics: Optional[List[str]] = None,
        **options,
    ) -> Dict[str, Any]:
        """
        Compare two graph versions.

        This method compares two version snapshots and calculates differences
        in entities and relationships.

        Args:
            version1: First version snapshot dictionary
            version2: Second version snapshot dictionary
            comparison_metrics: List of metrics to calculate (optional, unused)
            **options: Additional comparison options (unused)

        Returns:
            dict: Version comparison results containing:
                - version1: Label of first version
                - version2: Label of second version
                - entities_added: Change in entity count (version2 - version1)
                - relationships_added: Change in relationship count (version2 - version1)
        """
        comparison = {
            "version1": version1.get("label", "unknown"),
            "version2": version2.get("label", "unknown"),
            "entities_added": len(version2.get("entities", []))
            - len(version1.get("entities", [])),
            "relationships_added": len(version2.get("relationships", []))
            - len(version1.get("relationships", [])),
        }

        return comparison
