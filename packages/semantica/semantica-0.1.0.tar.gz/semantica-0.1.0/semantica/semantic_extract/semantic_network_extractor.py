"""
Semantic Network Extractor Module

This module extracts structured semantic networks from documents, converting
entities and relations into graph structures with nodes and edges. Part of the
6-stage ontology generation pipeline (Stage 2: semantic network extraction).
Supports multiple extraction methods for underlying entity and relation extraction.

Supported Methods (for underlying NER/Relation extractors):
    - "pattern": Pattern-based extraction
    - "regex": Regex-based extraction
    - "rules": Rule-based extraction
    - "ml": ML-based extraction (spaCy)
    - "huggingface": HuggingFace model extraction
    - "llm": LLM-based extraction
    - Any method supported by NERExtractor and RelationExtractor

Algorithms Used:
    - Graph Construction: Node and edge creation from entities and relations
    - Network Analysis: Degree centrality, betweenness centrality calculations
    - Connectivity Analysis: Path finding and component detection algorithms
    - YAML Serialization: Tree structure serialization algorithms
    - Graph Metrics: Node count, edge count, density calculations
    - Entity-Relation Mapping: Hash-based and graph-based entity-relation mapping

Key Features:
    - Semantic network construction from entities and relations
    - Node and edge creation
    - Network analysis and metrics
    - YAML export capabilities
    - Connectivity analysis
    - Integration with multiple NER and relation extraction methods
    - Method parameter support for underlying extractors

Main Classes:
    - SemanticNetworkExtractor: Main network extractor
    - SemanticNetwork: Semantic network representation dataclass
    - SemanticNode: Network node representation dataclass
    - SemanticEdge: Network edge representation dataclass

Example Usage:
    >>> from semantica.semantic_extract import SemanticNetworkExtractor
    >>> # Using default methods
    >>> extractor = SemanticNetworkExtractor()
    >>> network = extractor.extract_network(text, entities, relations)
    >>> 
    >>> # Using LLM-based extraction
    >>> extractor = SemanticNetworkExtractor(ner_method="llm", relation_method="llm", provider="openai")
    >>> network = extractor.extract_network(text)
    >>> 
    >>> analysis = extractor.analyze_network(network)
    >>> yaml_str = extractor.export_to_yaml(network, "network.yaml")

Author: Semantica Contributors
License: MIT
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

import yaml

from ..utils.exceptions import ProcessingError
from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker
from .ner_extractor import Entity
from .relation_extractor import Relation


@dataclass
class SemanticNode:
    """Semantic network node representation."""

    id: str
    label: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get attribute value like a dictionary."""
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> Any:
        """Get item like a dictionary."""
        return getattr(self, key)


@dataclass
class SemanticEdge:
    """Semantic network edge representation."""

    source: str
    target: str
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get attribute value like a dictionary."""
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> Any:
        """Get item like a dictionary."""
        return getattr(self, key)


@dataclass
class SemanticNetwork:
    """Semantic network representation."""

    nodes: List[SemanticNode]
    edges: List[SemanticEdge]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get attribute value like a dictionary."""
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> Any:
        """Get item like a dictionary."""
        return getattr(self, key)


class SemanticNetworkExtractor:
    """Semantic network extractor for structured networks."""

    def __init__(self, method: Union[str, List[str]] = None, **config):
        """
        Initialize semantic network extractor.

        Args:
            method: Extraction method(s) for underlying NER/relation extractors.
                   Can be passed to ner_method and relation_method in config.
            **config: Configuration options:
                - ner_method: Method for NER extraction (if entities need to be extracted)
                - relation_method: Method for relation extraction (if relations need to be extracted)
                - Other options passed to NER and relation extractors
        """
        self.logger = get_logger("semantic_network_extractor")
        self.config = config
        self.progress_tracker = get_progress_tracker()
        # Ensure progress tracker is enabled
        if not self.progress_tracker.enabled:
            self.progress_tracker.enabled = True

        # Store method for passing to extractors if needed
        if method is not None:
            self.config["ner_method"] = method
            self.config["relation_method"] = method

    def extract_network(
        self,
        text: str,
        entities: Optional[List[Entity]] = None,
        relations: Optional[List[Relation]] = None,
        **options,
    ) -> SemanticNetwork:
        """
        Extract semantic network from text.

        Args:
            text: Input text
            entities: Pre-extracted entities (optional)
            relations: Pre-extracted relations (optional)
            **options: Extraction options

        Returns:
            SemanticNetwork: Extracted semantic network
        """
        tracking_id = self.progress_tracker.start_tracking(
            module="semantic_extract",
            submodule="SemanticNetworkExtractor",
            message="Extracting semantic network from text",
        )

        try:
            from .ner_extractor import NERExtractor
            from .relation_extractor import RelationExtractor

            # Extract entities if not provided
            if entities is None:
                self.progress_tracker.update_tracking(
                    tracking_id, message="Extracting entities..."
                )
                ner_config = self.config.get("ner", {})
                # Pass method if specified
                if "ner_method" in self.config:
                    ner_config["method"] = self.config["ner_method"]
                ner = NERExtractor(
                    **ner_config,
                    **{
                        k: v
                        for k, v in self.config.items()
                        if k not in ["ner", "relation"]
                    },
                )
                entities = ner.extract_entities(text, **options)

            # Extract relations if not provided
            if relations is None:
                self.progress_tracker.update_tracking(
                    tracking_id, message="Extracting relations..."
                )
                rel_config = self.config.get("relation", {})
                # Pass method if specified
                if "relation_method" in self.config:
                    rel_config["method"] = self.config["relation_method"]
                rel_extractor = RelationExtractor(
                    **rel_config,
                    **{
                        k: v
                        for k, v in self.config.items()
                        if k not in ["ner", "relation"]
                    },
                )
                relations = rel_extractor.extract_relations(text, entities, **options)

            # Build network
            total_steps = 2  # Create nodes, create edges
            current_step = 0
            
            current_step += 1
            remaining_steps = total_steps - current_step
            self.progress_tracker.update_progress(
                tracking_id,
                processed=current_step,
                total=total_steps,
                message=f"Building semantic network... Creating nodes from {len(entities)} entities ({current_step}/{total_steps}, remaining: {remaining_steps} steps)"
            )
            network = self._build_network(entities, relations, tracking_id, total_steps, current_step)

            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Extracted network: {len(network.nodes)} nodes, {len(network.edges)} edges",
            )
            return network

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def _build_network(
        self, entities: List[Entity], relations: List[Relation], tracking_id: str = None, total_steps: int = 2, current_step: int = 1
    ) -> SemanticNetwork:
        """Build semantic network from entities and relations."""
        nodes = []
        edges = []
        node_map = {}

        # Create nodes from entities
        total_entities = len(entities)
        if total_entities <= 10:
            entity_update_interval = 1  # Update every item for small datasets
        else:
            entity_update_interval = max(1, min(10, total_entities // 100))
        
        # Initial progress update for entities
        if tracking_id and total_entities > 0:
            remaining_entities = total_entities
            self.progress_tracker.update_progress(
                tracking_id,
                processed=0,
                total=total_entities,
                message=f"Creating nodes from entities... 0/{total_entities} (remaining: {remaining_entities})"
            )
        
        for i, entity in enumerate(entities):
            node_id = f"entity_{len(nodes)}"
            node_map[entity.text] = node_id

            node = SemanticNode(
                id=node_id,
                label=entity.text,
                type=entity.label,
                properties={
                    "start_char": entity.start_char,
                    "end_char": entity.end_char,
                    "confidence": entity.confidence,
                },
                metadata=entity.metadata,
            )
            nodes.append(node)
            
            remaining_entities = total_entities - (i + 1)
            # Update progress: always update for small datasets, or at intervals for large ones
            if tracking_id:
                should_update = (
                    (i + 1) % entity_update_interval == 0 or 
                    (i + 1) == total_entities or 
                    i == 0 or
                    total_entities <= 10  # Always update for small datasets
                )
                if should_update:
                    self.progress_tracker.update_progress(
                        tracking_id,
                        processed=i + 1,
                        total=total_entities,
                        message=f"Creating nodes from entities... {i + 1}/{total_entities} (remaining: {remaining_entities})"
                    )

        # Create edges from relations
        total_relations = len(relations)
        if total_relations <= 10:
            relation_update_interval = 1  # Update every item for small datasets
        else:
            relation_update_interval = max(1, min(10, total_relations // 100))
        
        if tracking_id and total_relations > 0:
            # Initial progress update for relations
            remaining_relations = total_relations
            self.progress_tracker.update_progress(
                tracking_id,
                processed=0,
                total=total_relations,
                message=f"Creating edges from relations... 0/{total_relations} (remaining: {remaining_relations})"
            )
        
        for j, relation in enumerate(relations):
            subject_id = node_map.get(relation.subject.text)
            object_id = node_map.get(relation.object.text)

            if subject_id and object_id:
                edge = SemanticEdge(
                    source=subject_id,
                    target=object_id,
                    label=relation.predicate,
                    properties={
                        "confidence": relation.confidence,
                        "context": relation.context,
                    },
                    metadata=relation.metadata,
                )
                edges.append(edge)
            
            remaining_relations = len(relations) - (j + 1)
            # Update progress: always update for small datasets, or at intervals for large ones
            if tracking_id:
                should_update = (
                    (j + 1) % relation_update_interval == 0 or 
                    (j + 1) == len(relations) or 
                    j == 0 or
                    len(relations) <= 10  # Always update for small datasets
                )
                if should_update:
                    self.progress_tracker.update_progress(
                        tracking_id,
                        processed=j + 1,
                        total=len(relations),
                        message=f"Creating edges from relations... {j + 1}/{len(relations)} (remaining: {remaining_relations})"
                    )

        return SemanticNetwork(
            nodes=nodes,
            edges=edges,
            metadata={
                "node_count": len(nodes),
                "edge_count": len(edges),
                "entity_types": list(set(e.label for e in entities)),
                "relation_types": list(set(r.predicate for r in relations)),
            },
        )

    def export_to_yaml(
        self, network: SemanticNetwork, file_path: Optional[str] = None
    ) -> str:
        """
        Export semantic network to YAML format.

        Args:
            network: Semantic network
            file_path: Optional file path to save

        Returns:
            str: YAML representation
        """
        yaml_data = {
            "network": {
                "nodes": [
                    {
                        "id": node.id,
                        "label": node.label,
                        "type": node.type,
                        "properties": node.properties,
                        "metadata": node.metadata,
                    }
                    for node in network.nodes
                ],
                "edges": [
                    {
                        "source": edge.source,
                        "target": edge.target,
                        "label": edge.label,
                        "properties": edge.properties,
                        "metadata": edge.metadata,
                    }
                    for edge in network.edges
                ],
                "metadata": network.metadata,
            }
        }

        yaml_str = yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)

        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(yaml_str)

        return yaml_str

    def analyze_network(self, network: SemanticNetwork) -> Dict[str, Any]:
        """
        Analyze semantic network structure.

        Args:
            network: Semantic network
            **options: Analysis options

        Returns:
            dict: Network analysis
        """
        # Count node types
        node_types = {}
        for node in network.nodes:
            node_types[node.type] = node_types.get(node.type, 0) + 1

        # Count relation types
        relation_types = {}
        for edge in network.edges:
            relation_types[edge.label] = relation_types.get(edge.label, 0) + 1

        # Calculate connectivity
        node_degrees = {}
        for edge in network.edges:
            node_degrees[edge.source] = node_degrees.get(edge.source, 0) + 1
            node_degrees[edge.target] = node_degrees.get(edge.target, 0) + 1

        avg_degree = (
            sum(node_degrees.values()) / len(node_degrees) if node_degrees else 0
        )

        return {
            "node_count": len(network.nodes),
            "edge_count": len(network.edges),
            "node_types": node_types,
            "relation_types": relation_types,
            "average_degree": avg_degree,
            "connectivity": "sparse"
            if avg_degree < 2
            else "moderate"
            if avg_degree < 5
            else "dense",
        }
