"""
Context Graph Implementation

This module provides a synchronous, in-memory implementation of the GraphStore protocol,
designed for building and querying context graphs from conversations and entities.

It formalizes context as a graph of connections, enabling meaningful connections between
concepts, entities, and conversations.

Key Features:
    - In-memory GraphStore implementation
    - Entity and relationship extraction from conversations
    - BFS-based neighbor discovery
    - Type-based indexing
    - Export to dictionary format
"""

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union

from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker
from .entity_linker import EntityLinker


@dataclass
class ContextNode:
    """Context graph node (Internal implementation)."""

    node_id: str
    node_type: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        props = self.properties.copy()
        props.update(self.metadata)
        props["content"] = self.content
        return {"id": self.node_id, "type": self.node_type, "properties": props}


@dataclass
class ContextEdge:
    """Context graph edge (Internal implementation)."""

    source_id: str
    target_id: str
    edge_type: str
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.edge_type,
            "weight": self.weight,
            "properties": self.metadata,
        }


class ContextGraph:
    """
    In-memory implementation of context graph.

    Provides capabilities to build, store, and query a context graph.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize context graph.

        Args:
            config: Configuration dictionary
            **kwargs: Additional configuration options:
                - extract_entities: Extract entities from content (default: True)
                - extract_relationships: Extract relationships (default: True)
                - entity_linker: Entity linker instance
        """
        self.logger = get_logger("context_graph")
        self.config = config or {}
        self.config.update(kwargs)

        self.extract_entities = self.config.get("extract_entities", True)
        self.extract_relationships = self.config.get("extract_relationships", True)

        self.entity_linker = self.config.get("entity_linker") or EntityLinker()

        # Graph structure
        self.nodes: Dict[str, ContextNode] = {}
        self.edges: List[ContextEdge] = []

        # Adjacency list for efficient traversal: source_id -> list of edges
        self._adjacency: Dict[str, List[ContextEdge]] = defaultdict(list)

        # Indexes
        self.node_type_index: Dict[str, Set[str]] = defaultdict(set)
        self.edge_type_index: Dict[str, List[ContextEdge]] = defaultdict(list)

        # Progress tracker
        self.progress_tracker = get_progress_tracker()
        # Ensure progress tracker is enabled
        if not self.progress_tracker.enabled:
            self.progress_tracker.enabled = True

    # --- GraphStore Protocol Implementation ---

    def add_nodes(self, nodes: List[Dict[str, Any]]) -> int:
        """
        Add nodes to graph.

        Args:
            nodes: List of nodes to add (dicts with id, type, properties)

        Returns:
            Number of nodes added
        """
        count = 0
        for node in nodes:
            # Extract content from properties if not explicit
            node_props = node.get("properties", {})
            content = node_props.get("content", node.get("id"))
            metadata = {k: v for k, v in node_props.items() if k != "content"}

            internal_node = ContextNode(
                node_id=node.get("id"),
                node_type=node.get("type", "entity"),
                content=content,
                metadata=metadata,
                properties=node_props,
            )

            if self._add_internal_node(internal_node):
                count += 1
        return count

    def add_edges(self, edges: List[Dict[str, Any]]) -> int:
        """
        Add edges to graph.

        Args:
            edges: List of edges to add (dicts with source_id, target_id, type,
                weight, properties)

        Returns:
            Number of edges added
        """
        count = 0
        for edge in edges:
            internal_edge = ContextEdge(
                source_id=edge.get("source_id"),
                target_id=edge.get("target_id"),
                edge_type=edge.get("type", "related_to"),
                weight=edge.get("weight", 1.0),
                metadata=edge.get("properties", {}),
            )

            if self._add_internal_edge(internal_edge):
                count += 1
        return count

    def get_neighbors(self, node_id: str, hops: int = 1) -> List[Dict[str, Any]]:
        """
        Get neighbors of a node.

        Returns list of dicts with neighbor info.
        """
        if node_id not in self.nodes:
            return []

        neighbors = []
        visited = {node_id}
        queue = deque([(node_id, 0)])  # (current_id, current_hop)

        while queue:
            current_id, current_hop = queue.popleft()

            if current_hop >= hops:
                continue

            # Get outgoing edges
            outgoing_edges = self._adjacency.get(current_id, [])
            for edge in outgoing_edges:
                neighbor_id = edge.target_id
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, current_hop + 1))

                    if neighbor_id in self.nodes:
                        node = self.nodes[neighbor_id]
                        neighbors.append(
                            {
                                "id": node.node_id,
                                "type": node.node_type,
                                "content": node.content,
                                "relationship": edge.edge_type,
                                "weight": edge.weight,
                                "hop": current_hop + 1,
                            }
                        )

        return neighbors

    def query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a simple keyword search query on the graph nodes.

        Args:
            query: Keyword query string

        Returns:
            List of matching node dicts
        """
        results = []
        query_lower = query.lower().split()

        for node in self.nodes.values():
            content_lower = node.content.lower()
            if any(word in content_lower for word in query_lower):
                # Calculate simple score
                overlap = sum(1 for word in query_lower if word in content_lower)
                score = overlap / len(query_lower) if query_lower else 0.0

                results.append(
                    {
                        "node": node.to_dict(),
                        "score": score,
                        "content": node.content,
                    }
                )

        return sorted(results, key=lambda x: x["score"], reverse=True)

    def add_node(
        self,
        node_id: str,
        node_type: str,
        content: Optional[str] = None,
        **properties,
    ) -> bool:
        """
        Add a single node to the graph.

        Args:
            node_id: Unique identifier
            node_type: Node type (e.g., 'entity', 'concept')
            content: Node content/label
            **properties: Additional properties
        """
        content = content or node_id
        return self._add_internal_node(
            ContextNode(
                node_id=node_id,
                node_type=node_type,
                content=content,
                metadata=properties,
                properties=properties,
            )
        )

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str = "related_to",
        weight: float = 1.0,
        **properties,
    ) -> bool:
        """
        Add a single edge to the graph.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_type: Relationship type
            weight: Edge weight
            **properties: Additional properties
        """
        return self._add_internal_edge(
            ContextEdge(
                source_id=source_id,
                target_id=target_id,
                edge_type=edge_type,
                weight=weight,
                metadata=properties,
            )
        )

    def save_to_file(self, path: str) -> None:
        """
        Save context graph to file (JSON format).

        Args:
            path: File path to save to
        """
        import json

        data = {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Saved context graph to {path}")

    def load_from_file(self, path: str) -> None:
        """
        Load context graph from file (JSON format).

        Args:
            path: File path to load from
        """
        import json
        import os

        if not os.path.exists(path):
            self.logger.warning(f"File not found: {path}")
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Clear existing
        self.nodes.clear()
        self.edges.clear()
        self._adjacency.clear()
        self.node_type_index.clear()
        self.edge_type_index.clear()

        # Load nodes
        nodes = data.get("nodes", [])
        self.add_nodes(nodes)

        # Load edges
        edges = data.get("edges", [])
        self.add_edges(edges)

        self.logger.info(f"Loaded context graph from {path}")

    def find_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Find a node by ID."""
        node = self.nodes.get(node_id)
        if node:
            return {
                "id": node.node_id,
                "type": node.node_type,
                "content": node.content,
                "metadata": node.metadata,
            }
        return None

    def find_nodes(self, node_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find nodes, optionally filtered by type."""
        if node_type:
            node_ids = self.node_type_index.get(node_type, set())
            nodes = [self.nodes[nid] for nid in node_ids]
        else:
            nodes = self.nodes.values()

        return [
            {
                "id": n.node_id,
                "type": n.node_type,
                "content": n.content,
                "metadata": n.metadata,
            }
            for n in nodes
        ]

    def find_edges(self, edge_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find edges, optionally filtered by type."""
        if edge_type:
            edges = self.edge_type_index.get(edge_type, [])
        else:
            edges = self.edges

        return [
            {
                "source": e.source_id,
                "target": e.target_id,
                "type": e.edge_type,
                "weight": e.weight,
                "metadata": e.metadata,
            }
            for e in edges
        ]

    def stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "node_types": {k: len(v) for k, v in self.node_type_index.items()},
            "edge_types": {k: len(v) for k, v in self.edge_type_index.items()},
            "density": self.density(),
        }

    def density(self) -> float:
        """Calculate graph density."""
        n = len(self.nodes)
        if n < 2:
            return 0.0
        max_edges = n * (n - 1)  # Directed graph
        return len(self.edges) / max_edges

    # --- Internal Helpers ---

    def _add_internal_node(self, node: ContextNode) -> bool:
        """Internal method to add a node."""
        self.nodes[node.node_id] = node
        self.node_type_index[node.node_type].add(node.node_id)
        return True

    def _add_internal_edge(self, edge: ContextEdge) -> bool:
        """Internal method to add an edge."""
        # Ensure nodes exist
        if edge.source_id not in self.nodes:
            self._add_internal_node(
                ContextNode(edge.source_id, "entity", edge.source_id)
            )
        if edge.target_id not in self.nodes:
            self._add_internal_node(
                ContextNode(edge.target_id, "entity", edge.target_id)
            )

        self.edges.append(edge)
        self.edge_type_index[edge.edge_type].append(edge)
        self._adjacency[edge.source_id].append(edge)
        return True

    # --- Builder Methods (Legacy/Utility) ---

    def build_from_conversations(
        self,
        conversations: List[Union[str, Dict[str, Any]]],
        link_entities: bool = True,
        extract_intents: bool = False,
        extract_sentiments: bool = False,
        **options,
    ) -> Dict[str, Any]:
        """
        Build context graph from conversations and return dict representation.

        Args:
            conversations: List of conversation files or dictionaries
            ...

        Returns:
            Graph dictionary (nodes, edges)
        """
        tracking_id = self.progress_tracker.start_tracking(
            file=None,
            module="context",
            submodule="ContextGraph",
            message=f"Building graph from {len(conversations)} conversations",
        )

        try:
            for conv in conversations:
                conv_data = (
                    conv if isinstance(conv, dict) else self._load_conversation(conv)
                )
                self._process_conversation(
                    conv_data,
                    extract_intents=extract_intents,
                    extract_sentiments=extract_sentiments,
                )

            if link_entities:
                self._link_entities()

            self.progress_tracker.stop_tracking(tracking_id, status="completed")
            return self.to_dict()

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def build_from_entities_and_relationships(
        self,
        entities: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Build graph from entities and relationships.

        Args:
            entities: List of entity dictionaries
            relationships: List of relationship dictionaries
            **kwargs: Additional options

        Returns:
            Graph dictionary (nodes, edges)
        """
        tracking_id = self.progress_tracker.start_tracking(
            file=None,
            module="context",
            submodule="ContextGraph",
            message=(
                f"Building graph from {len(entities)} entities and "
                f"{len(relationships)} relationships"
            ),
        )

        try:
            # Add entities
            for entity in entities:
                entity_id = entity.get("id") or entity.get("entity_id")
                if entity_id:
                    self._add_internal_node(
                        ContextNode(
                            node_id=entity_id,
                            node_type=entity.get("type", "entity"),
                            content=entity.get("text")
                            or entity.get("label")
                            or entity_id,
                            metadata=entity,
                            properties=entity,
                        )
                    )

            # Add relationships
            for rel in relationships:
                source = rel.get("source_id")
                target = rel.get("target_id")
                if source and target:
                    self._add_internal_edge(
                        ContextEdge(
                            source_id=source,
                            target_id=target,
                            edge_type=rel.get("type", "related_to"),
                            weight=rel.get("confidence", 1.0),
                            metadata=rel,
                        )
                    )

            self.progress_tracker.stop_tracking(tracking_id, status="completed")
            return self.to_dict()

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def _process_conversation(self, conv_data: Dict[str, Any], **kwargs) -> None:
        """Process a single conversation."""
        conv_id = conv_data.get("id") or f"conv_{hash(str(conv_data)) % 10000}"

        # Add conversation node
        self._add_internal_node(
            ContextNode(
                node_id=conv_id,
                node_type="conversation",
                content=conv_data.get("content", "") or conv_data.get("summary", ""),
                metadata={"timestamp": conv_data.get("timestamp")},
            )
        )

        # Track name to ID mapping for relationship resolution
        name_to_id = {}

        # Extract entities
        if self.extract_entities:
            for entity in conv_data.get("entities", []):
                entity_id = entity.get("id") or entity.get("entity_id")
                entity_text = (
                    entity.get("text")
                    or entity.get("label")
                    or entity.get("name")
                    or entity_id
                )
                entity_type = entity.get("type", "entity")

                # Generate ID if missing
                if not entity_id and entity_text and self.entity_linker:
                    # Use EntityLinker to generate ID
                    if hasattr(self.entity_linker, "_generate_entity_id"):
                        entity_id = self.entity_linker._generate_entity_id(
                            entity_text, entity_type
                        )
                    else:
                        # Fallback ID generation
                        import hashlib

                        entity_hash = hashlib.md5(
                            f"{entity_text}_{entity_type}".encode()
                        ).hexdigest()[:12]
                        entity_id = f"{entity_type.lower()}_{entity_hash}"

                if entity_id:
                    if entity_text:
                        name_to_id[entity_text] = entity_id

                    self._add_internal_node(
                        ContextNode(
                            node_id=entity_id,
                            node_type="entity",
                            content=entity_text,
                            metadata={"type": entity_type, **entity},
                        )
                    )
                    self._add_internal_edge(
                        ContextEdge(
                            source_id=conv_id,
                            target_id=entity_id,
                            edge_type="mentions",
                        )
                    )

        # Extract relationships
        if self.extract_relationships:
            for rel in conv_data.get("relationships", []):
                source = rel.get("source_id")
                target = rel.get("target_id")

                # Resolve IDs from names if missing
                if not source and rel.get("source") and rel.get("source") in name_to_id:
                    source = name_to_id[rel.get("source")]

                if not target and rel.get("target") and rel.get("target") in name_to_id:
                    target = name_to_id[rel.get("target")]

                if source and target:
                    self._add_internal_edge(
                        ContextEdge(
                            source_id=source,
                            target_id=target,
                            edge_type=rel.get("type", "related_to"),
                            weight=rel.get("confidence", 1.0),
                        )
                    )

    def _link_entities(self) -> None:
        """Link similar entities using EntityLinker."""
        if not self.entity_linker:
            return

        entity_nodes = [n for n in self.nodes.values() if n.node_type == "entity"]
        for i, node1 in enumerate(entity_nodes):
            for node2 in entity_nodes[i + 1 :]:
                similarity = self.entity_linker._calculate_text_similarity(
                    node1.content.lower(), node2.content.lower()
                )
                if similarity >= self.entity_linker.similarity_threshold:
                    self._add_internal_edge(
                        ContextEdge(
                            source_id=node1.node_id,
                            target_id=node2.node_id,
                            edge_type="similar_to",
                            weight=similarity,
                        )
                    )

    def _load_conversation(self, file_path: str) -> Dict[str, Any]:
        """Load conversation from file."""
        from ..utils.helpers import read_json_file
        from pathlib import Path

        return read_json_file(Path(file_path))

    def to_dict(self) -> Dict[str, Any]:
        """Export graph to dictionary format."""
        return {
            "nodes": [
                {
                    "id": n.node_id,
                    "type": n.node_type,
                    "content": n.content,
                    "metadata": n.metadata,
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "source": e.source_id,
                    "target": e.target_id,
                    "type": e.edge_type,
                    "weight": e.weight,
                }
                for e in self.edges
            ],
            "statistics": {
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
            },
        }


# For backward compatibility
ContextGraphBuilder = ContextGraph
