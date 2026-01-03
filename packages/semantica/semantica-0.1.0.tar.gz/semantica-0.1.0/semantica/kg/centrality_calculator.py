"""
Centrality Calculator Module

This module provides comprehensive centrality measure calculations for knowledge
graphs, helping identify the most important or influential nodes in the graph.

Key Features:
    - Degree centrality: Measures node connectivity
    - Betweenness centrality: Measures node importance as a bridge
    - Closeness centrality: Measures average distance to all other nodes
    - Eigenvector centrality: Measures influence based on connections to important nodes
    - Centrality ranking and statistics

Example Usage:
    >>> from semantica.kg import CentralityCalculator
    >>> calculator = CentralityCalculator()
    >>> centrality = calculator.calculate_degree_centrality(graph)
    >>> all_centrality = calculator.calculate_all_centrality(graph)

Author: Semantica Contributors
License: MIT
"""

from collections import defaultdict, deque
from typing import Any, Dict, List, Optional

from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker


class CentralityCalculator:
    """
    Centrality measures calculation engine.

    This class calculates various centrality measures to identify important
    nodes in knowledge graphs. It supports multiple centrality types and
    can use NetworkX for optimized calculations when available.

    Supported Centrality Types:
        - degree: Number of connections (simplest, fastest)
        - betweenness: Importance as a bridge between nodes
        - closeness: Average distance to all other nodes
        - eigenvector: Influence based on connections to important nodes

    Example Usage:
        >>> calculator = CentralityCalculator()
        >>> # Calculate single type
        >>> degree = calculator.calculate_degree_centrality(graph)
        >>> # Calculate all types
        >>> all_centrality = calculator.calculate_all_centrality(graph)
    """

    def __init__(self, **config):
        """
        Initialize centrality calculator.

        Sets up the calculator with configuration and attempts to use NetworkX
        for optimized calculations if available, otherwise falls back to
        basic implementations.

        Args:
            **config: Configuration options:
                - calculation_config: Additional calculation configuration
        """
        self.logger = get_logger("centrality_calculator")
        self.config = config

        # Supported centrality types
        self.supported_centrality_types = [
            "degree",
            "betweenness",
            "closeness",
            "eigenvector",
        ]

        self.calculation_config = config.get("calculation_config", {})

        # Try to use NetworkX for optimized calculations (optional dependency)
        try:
            import networkx as nx

            self.nx = nx
            self.use_networkx = True
            self.logger.debug("NetworkX available, using optimized implementations")
        except ImportError:
            self.nx = None
            self.use_networkx = False
            self.logger.debug(
                "NetworkX not available, using basic implementations. "
                "Install with: pip install networkx"
            )

        # Initialize progress tracker
        self.progress_tracker = get_progress_tracker()
        # Ensure progress tracker is enabled
        if not self.progress_tracker.enabled:
            self.progress_tracker.enabled = True

        self.logger.info("Centrality calculator initialized")

    def calculate_degree_centrality(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate degree centrality for all nodes in the graph.

        Degree centrality measures the number of direct connections a node has.
        It's the simplest centrality measure and is normalized by the maximum
        possible degree (n-1 for n nodes).

        Args:
            graph: Input graph (dict with "entities" and "relationships" or NetworkX graph)

        Returns:
            Dictionary containing:
                - centrality: Dict mapping node IDs to centrality scores (0.0 to 1.0)
                - rankings: List of nodes ranked by centrality (highest first)
                - max_degree: Maximum degree in the graph
                - total_nodes: Total number of nodes

        Example:
            >>> result = calculator.calculate_degree_centrality(graph)
            >>> top_node = result["rankings"][0]["node"]
            >>> top_score = result["rankings"][0]["score"]
        """
        # Track centrality calculation
        tracking_id = self.progress_tracker.start_tracking(
            file=None,
            module="kg",
            submodule="CentralityCalculator",
            message="Calculating degree centrality",
        )

        try:
            self.logger.info("Calculating degree centrality")

            self.progress_tracker.update_tracking(
                tracking_id, message="Processing graph structure..."
            )
            # Use NetworkX if available for faster calculation
            if self.use_networkx:
                try:
                    nx_graph = self._to_networkx(graph)
                    centrality_dict = self.nx.degree_centrality(nx_graph)

                    # Convert to rankings
                    ranked = sorted(
                        centrality_dict.items(), key=lambda x: x[1], reverse=True
                    )

                    max_degree = (
                        max(dict(nx_graph.degree()).values())
                        if nx_graph.number_of_nodes() > 0
                        else 0
                    )

                    result = {
                        "centrality": centrality_dict,
                        "rankings": [
                            {"node": node, "score": score} for node, score in ranked
                        ],
                        "max_degree": max_degree,
                        "total_nodes": nx_graph.number_of_nodes(),
                    }
                    self.progress_tracker.stop_tracking(
                        tracking_id,
                        status="completed",
                        message=f"Calculated degree centrality for {nx_graph.number_of_nodes()} nodes",
                    )
                    return result
                except Exception as e:
                    self.logger.warning(
                        f"NetworkX calculation failed: {e}, using basic implementation"
                    )

            self.progress_tracker.update_tracking(
                tracking_id, message="Building adjacency list..."
            )
            # Basic implementation using adjacency list
            adjacency = self._build_adjacency(graph)

            self.progress_tracker.update_tracking(
                tracking_id, message="Calculating degrees..."
            )
            # Calculate raw degrees (number of connections per node)
            degrees = {}
            max_degree = 0

            for node in adjacency:
                degree = len(adjacency[node])
                degrees[node] = degree
                max_degree = max(max_degree, degree)

            self.progress_tracker.update_tracking(
                tracking_id, message="Normalizing centrality scores..."
            )
            # Calculate normalized centrality scores
            # Normalization: degree / (n - 1) where n is number of nodes
            centrality = {}
            num_nodes = len(adjacency)
            normalization = num_nodes - 1 if num_nodes > 1 else 1

            for node, degree in degrees.items():
                centrality[node] = degree / normalization if normalization > 0 else 0.0

            # Rank nodes by centrality (highest first)
            ranked = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

            self.logger.debug(
                f"Degree centrality calculated: {num_nodes} nodes, "
                f"max degree: {max_degree}"
            )

            result = {
                "centrality": centrality,
                "rankings": [{"node": node, "score": score} for node, score in ranked],
                "max_degree": max_degree,
                "total_nodes": num_nodes,
            }
            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Calculated degree centrality for {num_nodes} nodes",
            )
            return result

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def calculate_betweenness_centrality(self, graph):
        """
        Calculate betweenness centrality for all nodes.

        • Find shortest paths between all pairs
        • Count paths passing through each node
        • Normalize by total possible paths
        • Return betweenness centrality scores

        Args:
            graph: Input graph for centrality calculation

        Returns:
            dict: Node centrality scores and rankings
        """
        self.logger.info("Calculating betweenness centrality")

        if self.use_networkx:
            try:
                nx_graph = self._to_networkx(graph)
                centrality = self.nx.betweenness_centrality(nx_graph)
                ranked = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

                return {
                    "centrality": centrality,
                    "rankings": [
                        {"node": node, "score": score} for node, score in ranked
                    ],
                }
            except Exception as e:
                self.logger.warning(
                    f"NetworkX calculation failed: {e}, using basic implementation"
                )

        # Basic implementation using BFS
        adjacency = self._build_adjacency(graph)
        nodes = list(adjacency.keys())
        betweenness = {node: 0.0 for node in nodes}

        # For each pair of nodes, find shortest paths
        for source in nodes:
            # BFS to find shortest paths
            paths = self._bfs_shortest_paths(adjacency, source)

            for target in nodes:
                if source == target:
                    continue

                if target in paths:
                    # Count paths through each node
                    for path in paths[target]:
                        for node in path[1:-1]:  # Exclude source and target
                            if node in betweenness:
                                betweenness[node] += 1.0

        # Normalize
        n = len(nodes)
        if n > 2:
            normalization = (n - 1) * (n - 2) / 2
            for node in betweenness:
                betweenness[node] /= normalization if normalization > 0 else 1

        ranked = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)

        return {
            "centrality": betweenness,
            "rankings": [{"node": node, "score": score} for node, score in ranked],
        }

    def calculate_closeness_centrality(self, graph):
        """
        Calculate closeness centrality for all nodes.

        • Calculate shortest path distances
        • Compute average distance to all nodes
        • Normalize by graph size
        • Return closeness centrality scores

        Args:
            graph: Input graph for centrality calculation

        Returns:
            dict: Node centrality scores and rankings
        """
        self.logger.info("Calculating closeness centrality")

        if self.use_networkx:
            try:
                nx_graph = self._to_networkx(graph)
                centrality = self.nx.closeness_centrality(nx_graph)
                ranked = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

                return {
                    "centrality": centrality,
                    "rankings": [
                        {"node": node, "score": score} for node, score in ranked
                    ],
                }
            except Exception as e:
                self.logger.warning(
                    f"NetworkX calculation failed: {e}, using basic implementation"
                )

        # Basic implementation
        adjacency = self._build_adjacency(graph)
        nodes = list(adjacency.keys())
        closeness = {}

        for node in nodes:
            # BFS to find distances
            distances = self._bfs_distances(adjacency, node)

            # Calculate sum of distances
            total_distance = sum(distances.values())
            reachable = len(distances) - 1  # Exclude self

            if reachable > 0 and total_distance > 0:
                # Closeness = (n-1) / sum of distances
                closeness[node] = reachable / total_distance
            else:
                closeness[node] = 0.0

        ranked = sorted(closeness.items(), key=lambda x: x[1], reverse=True)

        return {
            "centrality": closeness,
            "rankings": [{"node": node, "score": score} for node, score in ranked],
        }

    def calculate_eigenvector_centrality(self, graph, max_iter=100, tol=1e-6):
        """
        Calculate eigenvector centrality for all nodes.

        • Compute adjacency matrix eigenvalues
        • Calculate eigenvector centrality
        • Handle convergence and stability
        • Return eigenvector centrality scores

        Args:
            graph: Input graph for centrality calculation
            max_iter: Maximum iterations
            tol: Convergence tolerance

        Returns:
            dict: Node centrality scores and rankings
        """
        self.logger.info("Calculating eigenvector centrality")

        if self.use_networkx:
            try:
                nx_graph = self._to_networkx(graph)
                centrality = self.nx.eigenvector_centrality(
                    nx_graph, max_iter=max_iter, tol=tol
                )
                ranked = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

                return {
                    "centrality": centrality,
                    "rankings": [
                        {"node": node, "score": score} for node, score in ranked
                    ],
                }
            except Exception as e:
                self.logger.warning(
                    f"NetworkX calculation failed: {e}, using basic implementation"
                )

        # Basic power iteration method
        import numpy as np

        adjacency = self._build_adjacency(graph)
        nodes = sorted(adjacency.keys())
        n = len(nodes)
        node_to_index = {node: i for i, node in enumerate(nodes)}

        # Build adjacency matrix
        A = np.zeros((n, n))
        for i, node in enumerate(nodes):
            for neighbor in adjacency[node]:
                if neighbor in node_to_index:
                    j = node_to_index[neighbor]
                    A[i, j] = 1.0
                    A[j, i] = 1.0

        # Power iteration
        x = np.ones(n) / np.sqrt(n)

        for _ in range(max_iter):
            x_new = A @ x
            norm = np.linalg.norm(x_new)
            if norm == 0:
                break
            x_new = x_new / norm

            if np.linalg.norm(x_new - x) < tol:
                break
            x = x_new

        # Normalize
        centrality = {nodes[i]: float(x[i]) for i in range(n)}

        # Normalize to [0, 1]
        max_val = max(centrality.values()) if centrality.values() else 1.0
        if max_val > 0:
            centrality = {node: score / max_val for node, score in centrality.items()}

        ranked = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

        return {
            "centrality": centrality,
            "rankings": [{"node": node, "score": score} for node, score in ranked],
        }

    def calculate_all_centrality(self, graph, centrality_types=None):
        """
        Calculate all supported centrality measures.

        • Calculate multiple centrality types
        • Combine centrality results
        • Provide comprehensive centrality analysis
        • Return unified centrality results

        Args:
            graph: Input graph for centrality calculation
            centrality_types: List of centrality types to calculate

        Returns:
            dict: Comprehensive centrality analysis results
        """
        self.logger.info("Calculating all centrality measures")

        centrality_types = centrality_types or self.supported_centrality_types
        results = {}

        if "degree" in centrality_types:
            results["degree"] = self.calculate_degree_centrality(graph)

        if "betweenness" in centrality_types:
            results["betweenness"] = self.calculate_betweenness_centrality(graph)

        if "closeness" in centrality_types:
            results["closeness"] = self.calculate_closeness_centrality(graph)

        if "eigenvector" in centrality_types:
            results["eigenvector"] = self.calculate_eigenvector_centrality(graph)

        return {
            "centrality_measures": results,
            "types_calculated": list(results.keys()),
            "total_nodes": len(self._build_adjacency(graph)),
        }

    def _build_adjacency(self, graph) -> Dict[str, List[str]]:
        """Build adjacency list from graph."""
        adjacency = defaultdict(list)

        # Extract relationships
        relationships = []
        if hasattr(graph, "relationships"):
            relationships = graph.relationships
        elif hasattr(graph, "get_relationships"):
            relationships = graph.get_relationships()
        elif isinstance(graph, dict):
            relationships = graph.get("relationships", [])

        # Build adjacency
        for rel in relationships:
            source = rel.get("source") or rel.get("subject")
            target = rel.get("target") or rel.get("object")

            if source and target:
                if target not in adjacency[source]:
                    adjacency[source].append(target)
                if source not in adjacency[target]:
                    adjacency[target].append(source)

        return dict(adjacency)

    def _to_networkx(self, graph):
        """Convert graph to NetworkX format."""
        adjacency = self._build_adjacency(graph)
        nx_graph = self.nx.Graph()

        for source, targets in adjacency.items():
            for target in targets:
                nx_graph.add_edge(source, target)

        return nx_graph

    def _bfs_distances(
        self, adjacency: Dict[str, List[str]], start: str
    ) -> Dict[str, int]:
        """Calculate distances using BFS."""
        distances = {start: 0}
        queue = deque([start])

        while queue:
            node = queue.popleft()
            for neighbor in adjacency.get(node, []):
                if neighbor not in distances:
                    distances[neighbor] = distances[node] + 1
                    queue.append(neighbor)

        return distances

    def _bfs_shortest_paths(
        self, adjacency: Dict[str, List[str]], start: str
    ) -> Dict[str, List[List[str]]]:
        """Find all shortest paths using BFS."""
        paths = {start: [[start]]}
        queue = deque([start])
        visited = {start}

        while queue:
            node = queue.popleft()
            for neighbor in adjacency.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    # Find paths to neighbor
                    neighbor_paths = []
                    for path in paths[node]:
                        neighbor_paths.append(path + [neighbor])
                    paths[neighbor] = neighbor_paths
                    queue.append(neighbor)
                elif neighbor in paths:
                    # Check if this is a shortest path
                    current_length = len(paths[neighbor][0])
                    new_length = len(paths[node][0]) + 1
                    if new_length == current_length:
                        # Add alternative paths
                        for path in paths[node]:
                            new_path = path + [neighbor]
                            if new_path not in paths[neighbor]:
                                paths[neighbor].append(new_path)

        return paths
