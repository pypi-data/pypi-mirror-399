"""
Knowledge Graph Methods Module

This module provides all knowledge graph methods as simple, reusable functions for
building, analyzing, and managing knowledge graphs. It supports multiple
approaches and integrates with the method registry for extensibility.

Supported Methods:

Knowledge Graph Building:
    - "default": Default graph building using GraphBuilder
    - "incremental": Incremental graph building
    - "temporal": Temporal knowledge graph building

Graph Analysis:
    - "default": Comprehensive graph analysis
    - "centrality": Centrality-focused analysis
    - "community": Community-focused analysis
    - "connectivity": Connectivity-focused analysis

Entity Resolution:
    - "fuzzy": Fuzzy string matching resolution
    - "exact": Exact string matching resolution
    - "semantic": Semantic similarity matching resolution

Conflict Detection:
    - "default": Comprehensive conflict detection
    - "value": Value conflict detection only
    - "relationship": Relationship conflict detection only

Centrality Calculation:
    - "degree": Degree centrality
    - "betweenness": Betweenness centrality
    - "closeness": Closeness centrality
    - "eigenvector": Eigenvector centrality
    - "all": All centrality measures

Community Detection:
    - "louvain": Louvain algorithm
    - "leiden": Leiden algorithm
    - "overlapping": Overlapping community detection

Connectivity Analysis:
    - "default": Comprehensive connectivity analysis
    - "components": Connected components only
    - "paths": Path finding only
    - "bridges": Bridge detection only

Deduplication:
    - "default": Default deduplication
    - "entities": Entity deduplication only
    - "relationships": Relationship deduplication only

Temporal Queries:
    - "time_point": Time-point queries
    - "time_range": Time-range queries
    - "pattern": Temporal pattern detection
    - "evolution": Graph evolution analysis

Algorithms Used:

Knowledge Graph Construction:
    - Graph Building: Entity-relationship graph construction from multiple sources
    - Entity Resolution: Fuzzy string matching, exact matching, semantic similarity matching for duplicate detection
    - Conflict Detection: Value conflict detection (same entity with different property values), relationship conflict detection
    - Conflict Resolution: Highest confidence strategy, source-based resolution
    - Temporal Graph Support: Time-aware edge creation with valid_from/valid_until timestamps
    - Temporal Granularity: Time normalization (second, minute, hour, day, week, month, year)
    - Entity Merging: Property aggregation, metadata merging, provenance tracking
    - Incremental Building: Batch processing for large graphs

Graph Analysis:
    - Degree Centrality: Normalized degree calculation (degree / (n-1)) for connectivity measure
    - Betweenness Centrality: Shortest path counting (BFS-based), path normalization by (n-1)*(n-2)/2
    - Closeness Centrality: Average distance calculation, (n-1) / sum of distances normalization
    - Eigenvector Centrality: Power iteration method, adjacency matrix eigenvalue computation, convergence tolerance
    - Community Detection: Louvain algorithm (greedy modularity optimization), Leiden algorithm (with refinement step)
    - Overlapping Communities: K-clique community detection, dense subgraph detection
    - Modularity Calculation: Q = (1/2m) * Σ(A_ij - k_i*k_j/2m) * δ(c_i, c_j)
    - Graph Connectivity: DFS-based connected component detection, component size analysis
    - Bridge Detection: Edge removal and connectivity change detection
    - Path Finding: BFS shortest path algorithm, all-pairs shortest paths computation
    - Graph Density: E / (n*(n-1)/2) calculation for undirected graphs
    - Structure Classification: Density-based classification (sparse, moderate, dense, disconnected)

Entity Resolution:
    - Duplicate Detection: Similarity-based grouping using threshold matching
    - Fuzzy Matching: String similarity algorithms (Levenshtein, Jaro-Winkler)
    - Semantic Matching: Embedding-based similarity for semantic entity matching
    - Entity Merging: Property conflict resolution, metadata aggregation
    - ID Normalization: Canonical ID assignment for merged entities

Conflict Detection:
    - Value Conflict Detection: Property value comparison, unique value set extraction
    - Relationship Conflict Detection: Relationship property comparison, conflict identification
    - Source Tracking: Multi-source conflict tracking, provenance-based conflict resolution
    - Conflict Categorization: Value conflicts vs relationship conflicts

Temporal Operations:
    - Time-Point Queries: Temporal filtering using valid_from/valid_until comparison
    - Time-Range Queries: Interval overlap detection, union/intersection aggregation
    - Temporal Pattern Detection: Sequence detection, cycle detection, trend analysis
    - Graph Evolution Analysis: Time-series relationship counting, diversity metrics, stability measures
    - Temporal Path Finding: BFS with temporal validity constraints
    - Version Management: Snapshot creation, version comparison, timestamp-based versioning

Deduplication:
    - Duplicate Group Detection: Similarity-based clustering, threshold-based grouping
    - Entity Merging: Property aggregation strategies, metadata merging
    - Provenance Tracking: Source tracking for merged entities, lineage maintenance

Key Features:
    - Multiple KG operation methods
    - Knowledge graph building with method dispatch
    - Method dispatchers with registry support
    - Custom method registration capability
    - Consistent interface across all methods

Main Functions:
    - build_kg: Knowledge graph building wrapper
    - analyze_graph: Graph analysis wrapper
    - resolve_entities: Entity resolution wrapper
    - calculate_centrality: Centrality calculation wrapper
    - detect_communities: Community detection wrapper
    - analyze_connectivity: Connectivity analysis wrapper
    - query_temporal: Temporal query wrapper
    - get_kg_method: Get KG method by name
    - list_available_methods: List registered methods

Note: Conflict detection and deduplication have been moved to dedicated modules.
    Use semantica.conflicts for conflict detection and semantica.deduplication for deduplication.

Example Usage:
    >>> from semantica.kg.methods import build_kg, analyze_graph, calculate_centrality
    >>> kg = build_kg(sources, method="default")
    >>> analysis = analyze_graph(kg, method="default")
    >>> centrality = calculate_centrality(kg, method="degree")
"""

from typing import Any, Callable, Dict, List, Optional, Union

from ..utils.exceptions import ConfigurationError, ProcessingError
from ..utils.logging import get_logger
from .centrality_calculator import CentralityCalculator
from .community_detector import CommunityDetector
from .config import kg_config
from .connectivity_analyzer import ConnectivityAnalyzer
from .entity_resolver import EntityResolver
from .graph_analyzer import GraphAnalyzer
from .graph_builder import GraphBuilder
from .registry import method_registry
from .temporal_query import TemporalGraphQuery

logger = get_logger("kg_methods")


def build_kg(
    sources: Union[List[Any], Any], method: str = "default", **kwargs
) -> Dict[str, Any]:
    """
    Build knowledge graph from sources (convenience function).

    This is a user-friendly wrapper that builds a knowledge graph using the specified method.

    Args:
        sources: List of sources (documents, entities, relationships, or dicts with entities/relationships)
        method: Building method (default: "default")
            - "default": Use GraphBuilder with default settings
            - "incremental": Incremental building
            - "temporal": Temporal knowledge graph building
        **kwargs: Additional options passed to GraphBuilder

    Returns:
        Dictionary containing:
            - entities: List of entities
            - relationships: List of relationships
            - metadata: Graph metadata including counts and timestamps

    Examples:
        >>> from semantica.kg.methods import build_kg
        >>> kg = build_kg(sources, method="default")
        >>> temporal_kg = build_kg(sources, method="temporal", enable_temporal=True)
    """
    # Check for custom method in registry
    custom_method = method_registry.get("build", method)
    if custom_method:
        try:
            return custom_method(sources, **kwargs)
        except Exception as e:
            logger.warning(
                f"Custom method {method} failed: {e}, falling back to default"
            )

    try:
        # Get config
        config = kg_config.get_method_config("build")
        config.update(kwargs)

        builder = GraphBuilder(**config)
        return builder.build(sources, **kwargs)

    except Exception as e:
        logger.error(f"Failed to build knowledge graph: {e}")
        raise


def analyze_graph(
    graph: Dict[str, Any], method: str = "default", **kwargs
) -> Dict[str, Any]:
    """
    Analyze knowledge graph (convenience function).

    This is a user-friendly wrapper that analyzes a knowledge graph using the specified method.

    Args:
        graph: Knowledge graph (dict with "entities" and "relationships")
        method: Analysis method (default: "default")
            - "default": Comprehensive analysis
            - "centrality": Centrality-focused analysis
            - "community": Community-focused analysis
            - "connectivity": Connectivity-focused analysis
        **kwargs: Additional options passed to GraphAnalyzer

    Returns:
        Dictionary containing analysis results

    Examples:
        >>> from semantica.kg.methods import analyze_graph
        >>> analysis = analyze_graph(kg, method="default")
        >>> centrality_analysis = analyze_graph(kg, method="centrality")
    """
    # Check for custom method in registry
    custom_method = method_registry.get("analyze", method)
    if custom_method:
        try:
            return custom_method(graph, **kwargs)
        except Exception as e:
            logger.warning(
                f"Custom method {method} failed: {e}, falling back to default"
            )

    try:
        # Get config
        config = kg_config.get_method_config("analyze")
        config.update(kwargs)

        analyzer = GraphAnalyzer(**config)
        return analyzer.analyze_graph(graph, **kwargs)

    except Exception as e:
        logger.error(f"Failed to analyze graph: {e}")
        raise


def resolve_entities(
    entities: List[Dict[str, Any]], method: str = "fuzzy", **kwargs
) -> List[Dict[str, Any]]:
    """
    Resolve and disambiguate entities (convenience function).

    This is a user-friendly wrapper that resolves entities using the specified method.

    Args:
        entities: List of entity dictionaries to resolve
        method: Resolution method (default: "fuzzy")
            - "fuzzy": Fuzzy string matching resolution
            - "exact": Exact string matching resolution
            - "semantic": Semantic similarity matching resolution
        **kwargs: Additional options passed to EntityResolver

    Returns:
        List of resolved entities with duplicates merged

    Examples:
        >>> from semantica.kg.methods import resolve_entities
        >>> resolved = resolve_entities(entities, method="fuzzy")
        >>> semantic_resolved = resolve_entities(entities, method="semantic")
    """
    # Check for custom method in registry
    custom_method = method_registry.get("resolve", method)
    if custom_method:
        try:
            return custom_method(entities, **kwargs)
        except Exception as e:
            logger.warning(f"Custom method {method} failed: {e}, falling back to fuzzy")
            method = "fuzzy"

    try:
        # Get config
        config = kg_config.get_method_config("resolve")
        config.update(kwargs)

        resolver = EntityResolver(strategy=method, **config)
        return resolver.resolve_entities(entities)

    except Exception as e:
        logger.error(f"Failed to resolve entities: {e}")
        raise


def calculate_centrality(
    graph: Dict[str, Any], method: str = "degree", **kwargs
) -> Dict[str, Any]:
    """
    Calculate centrality measures (convenience function).

    This is a user-friendly wrapper that calculates centrality using the specified method.

    Args:
        graph: Knowledge graph to analyze
        method: Centrality method (default: "degree")
            - "degree": Degree centrality
            - "betweenness": Betweenness centrality
            - "closeness": Closeness centrality
            - "eigenvector": Eigenvector centrality
            - "all": All centrality measures
        **kwargs: Additional options passed to CentralityCalculator

    Returns:
        Dictionary containing centrality results

    Examples:
        >>> from semantica.kg.methods import calculate_centrality
        >>> degree = calculate_centrality(kg, method="degree")
        >>> all_centrality = calculate_centrality(kg, method="all")
    """
    # Check for custom method in registry
    custom_method = method_registry.get("centrality", method)
    if custom_method:
        try:
            return custom_method(graph, **kwargs)
        except Exception as e:
            logger.warning(
                f"Custom method {method} failed: {e}, falling back to degree"
            )
            method = "degree"

    try:
        # Get config
        config = kg_config.get_method_config("centrality")
        config.update(kwargs)

        calculator = CentralityCalculator(**config)

        if method == "degree":
            return calculator.calculate_degree_centrality(graph)
        elif method == "betweenness":
            return calculator.calculate_betweenness_centrality(graph)
        elif method == "closeness":
            return calculator.calculate_closeness_centrality(graph)
        elif method == "eigenvector":
            return calculator.calculate_eigenvector_centrality(graph)
        elif method == "all":
            return calculator.calculate_all_centrality(graph)
        else:
            raise ProcessingError(f"Unknown centrality method: {method}")

    except Exception as e:
        logger.error(f"Failed to calculate centrality: {e}")
        raise


def detect_communities(
    graph: Dict[str, Any], method: str = "louvain", **kwargs
) -> Dict[str, Any]:
    """
    Detect communities in knowledge graph (convenience function).

    This is a user-friendly wrapper that detects communities using the specified method.

    Args:
        graph: Knowledge graph to analyze
        method: Community detection method (default: "louvain")
            - "louvain": Louvain algorithm
            - "leiden": Leiden algorithm
            - "overlapping": Overlapping community detection
        **kwargs: Additional options passed to CommunityDetector

    Returns:
        Dictionary containing community detection results

    Examples:
        >>> from semantica.kg.methods import detect_communities
        >>> communities = detect_communities(kg, method="louvain")
        >>> overlapping = detect_communities(kg, method="overlapping")
    """
    # Check for custom method in registry
    custom_method = method_registry.get("community", method)
    if custom_method:
        try:
            return custom_method(graph, **kwargs)
        except Exception as e:
            logger.warning(
                f"Custom method {method} failed: {e}, falling back to louvain"
            )
            method = "louvain"

    try:
        # Get config
        config = kg_config.get_method_config("community")
        config.update(kwargs)

        detector = CommunityDetector(**config)
        return detector.detect_communities(graph, algorithm=method, **kwargs)

    except Exception as e:
        logger.error(f"Failed to detect communities: {e}")
        raise


def analyze_connectivity(
    graph: Dict[str, Any], method: str = "default", **kwargs
) -> Dict[str, Any]:
    """
    Analyze graph connectivity (convenience function).

    This is a user-friendly wrapper that analyzes connectivity using the specified method.

    Args:
        graph: Knowledge graph to analyze
        method: Connectivity analysis method (default: "default")
            - "default": Comprehensive connectivity analysis
            - "components": Connected components only
            - "paths": Path finding only
            - "bridges": Bridge detection only
        **kwargs: Additional options passed to ConnectivityAnalyzer

    Returns:
        Dictionary containing connectivity analysis results

    Examples:
        >>> from semantica.kg.methods import analyze_connectivity
        >>> connectivity = analyze_connectivity(kg, method="default")
        >>> components = analyze_connectivity(kg, method="components")
    """
    # Check for custom method in registry
    custom_method = method_registry.get("connectivity", method)
    if custom_method:
        try:
            return custom_method(graph, **kwargs)
        except Exception as e:
            logger.warning(
                f"Custom method {method} failed: {e}, falling back to default"
            )

    try:
        # Get config
        config = kg_config.get_method_config("connectivity")
        config.update(kwargs)

        analyzer = ConnectivityAnalyzer(**config)

        if method == "components":
            return analyzer.find_connected_components(graph)
        elif method == "paths":
            source = kwargs.get("source")
            target = kwargs.get("target")
            return analyzer.calculate_shortest_paths(
                graph, source=source, target=target
            )
        elif method == "bridges":
            return analyzer.identify_bridges(graph)
        else:
            return analyzer.analyze_connectivity(graph)

    except Exception as e:
        logger.error(f"Failed to analyze connectivity: {e}")
        raise


def query_temporal(
    graph: Dict[str, Any], query: str = "", method: str = "time_point", **kwargs
) -> Dict[str, Any]:
    """
    Query temporal knowledge graph (convenience function).

    This is a user-friendly wrapper that queries a temporal knowledge graph using the specified method.

    Args:
        graph: Knowledge graph to query
        query: Query string (optional, depends on method)
        method: Temporal query method (default: "time_point")
            - "time_point": Time-point queries
            - "time_range": Time-range queries
            - "pattern": Temporal pattern detection
            - "evolution": Graph evolution analysis
        **kwargs: Additional options passed to TemporalGraphQuery

    Returns:
        Dictionary containing query results

    Examples:
        >>> from semantica.kg.methods import query_temporal
        >>> result = query_temporal(kg, at_time="2024-01-01", method="time_point")
        >>> patterns = query_temporal(kg, pattern="sequence", method="pattern")
    """
    # Check for custom method in registry
    custom_method = method_registry.get("temporal", method)
    if custom_method:
        try:
            return custom_method(graph, query=query, **kwargs)
        except Exception as e:
            logger.warning(
                f"Custom method {method} failed: {e}, falling back to time_point"
            )
            method = "time_point"

    try:
        # Get config
        config = kg_config.get_method_config("temporal")
        config.update(kwargs)

        query_engine = TemporalGraphQuery(**config)

        if method == "time_point":
            at_time = kwargs.get("at_time")
            return query_engine.query_at_time(graph, query, at_time=at_time, **kwargs)
        elif method == "time_range":
            start_time = kwargs.get("start_time")
            end_time = kwargs.get("end_time")
            return query_engine.query_time_range(
                graph, query, start_time, end_time, **kwargs
            )
        elif method == "pattern":
            pattern = kwargs.get("pattern", "sequence")
            return query_engine.query_temporal_pattern(graph, pattern, **kwargs)
        elif method == "evolution":
            return query_engine.analyze_evolution(graph, **kwargs)
        else:
            raise ProcessingError(f"Unknown temporal query method: {method}")

    except Exception as e:
        logger.error(f"Failed to query temporal graph: {e}")
        raise


def get_kg_method(task: str, method: str) -> Optional[Callable]:
    """
    Get KG method by task and name.

    Args:
        task: Task type ("build", "analyze", "resolve", "validate", "conflict", "centrality", "community", "connectivity", "deduplicate", "temporal")
        method: Method name

    Returns:
        Method function or None

    Examples:
        >>> from semantica.kg.methods import get_kg_method
        >>> build_fn = get_kg_method("build", "default")
    """
    return method_registry.get(task, method)


def list_available_methods(task: Optional[str] = None) -> Dict[str, List[str]]:
    """
    List all available KG methods.

    Args:
        task: Optional task type to filter by

    Returns:
        Dictionary mapping task types to method names

    Examples:
        >>> from semantica.kg.methods import list_available_methods
        >>> all_methods = list_available_methods()
        >>> build_methods = list_available_methods("build")
    """
    return method_registry.list_all(task)
