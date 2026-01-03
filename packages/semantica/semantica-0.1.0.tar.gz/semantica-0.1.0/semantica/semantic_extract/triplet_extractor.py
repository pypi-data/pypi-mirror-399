"""
RDF Triplet Extraction Module

This module provides comprehensive RDF triplet extraction capabilities, enabling
conversion of entities and relations into RDF triplets using multiple extraction
methods, with validation and serialization support.

Supported Methods:
    - "pattern": Pattern-based triplet extraction from relations (default)
    - "rules": Rule-based triplet extraction using linguistic rules
    - "huggingface": Custom HuggingFace triplet extraction models
    - "llm": LLM-based triplet extraction using various providers

Algorithms Used:
    - Pattern Matching: Regex-based subject-predicate-object extraction
    - Rule-based Extraction: Linguistic rule application for triplet formation
    - Sequence-to-Sequence Models: Transformer-based seq2seq for triplet generation
    - Large Language Models: GPT, Claude, Gemini for structured triplet extraction
    - RDF Serialization: Graph serialization algorithms (Turtle, N-Triples, JSON-LD)
    - URI Normalization: String normalization and URI formatting algorithms

Key Features:
    - Multiple extraction methods:
        * Pattern-based: Pattern matching for triplet extraction (default)
        * Rules-based: Rule-based triplet extraction
        * HuggingFace: Custom HuggingFace triplet models
        * LLM-based: LLM-powered triplet extraction
    - Fallback chain support: Try methods in order until one succeeds
    - RDF triplet generation from entities and relations
    - Subject-predicate-object extraction
    - Triplet validation and quality checking
    - RDF serialization (Turtle, N-Triples, JSON-LD, RDF/XML)
    - Batch triplet processing
    - URI formatting and normalization
    - Quality assessment and scoring

Main Classes:
    - TripletExtractor: Main triplet extraction coordinator with method selection
    - TripletValidator: Triplet validation engine
    - RDFSerializer: RDF serialization handler
    - TripletQualityChecker: Triplet quality assessment
    - Triplet: RDF triplet representation dataclass

Example Usage:
    >>> from semantica.semantic_extract import TripletExtractor
    >>> # Using pattern method (default)
    >>> extractor = TripletExtractor(method="pattern")
    >>> triplets = extractor.extract_triplets(text, entities, relations)
    >>> 
    >>> # Using LLM method
    >>> extractor = TripletExtractor(method="llm", provider="openai", llm_model="gpt-4")
    >>> triplets = extractor.extract_triplets(text, entities, relations)
    >>> 
    >>> # Using HuggingFace model
    >>> extractor = TripletExtractor(method="huggingface", huggingface_model="custom/triplet-model")
    >>> triplets = extractor.extract_triplets(text)
    >>> 
    >>> # Serialize to RDF
    >>> rdf_turtle = extractor.serialize_triplets(triplets, format="turtle")
    >>> validated = extractor.validate_triplets(triplets)

Author: Semantica Contributors
License: MIT
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote

from ..utils.exceptions import ProcessingError, ValidationError
from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker
from .ner_extractor import Entity
from .relation_extractor import Relation


@dataclass
class Triplet:
    """RDF triplet representation."""

    subject: str
    predicate: str
    object: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get attribute value like a dictionary."""
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> Any:
        """Get item like a dictionary."""
        return getattr(self, key)


class TripletExtractor:
    """RDF triplet extraction handler."""

    def __init__(
        self,
        method: Union[str, List[str]] = "pattern",
        include_temporal: bool = False,
        include_provenance: bool = False,
        config=None,
        **kwargs
    ):
        """
        Initialize triplet extractor.

        Args:
            method: Extraction method(s). Can be:
                - "pattern": Pattern-based extraction (default)
                - "rules": Rule-based extraction
                - "huggingface": HuggingFace model
                - "llm": LLM-based extraction
                - List of methods for fallback chain
            include_temporal: Whether to include temporal information in triplets
            include_provenance: Whether to track source sentences for provenance
            config: Legacy config dict (deprecated, use kwargs)
            **kwargs: Configuration options:
                - model: Model name (for HuggingFace methods)
                - huggingface_model: HuggingFace model name
                - provider: LLM provider (for LLM method)
                - llm_model: LLM model name
                - device: Device for HuggingFace models
                - min_confidence: Minimum confidence threshold
                - validate: Enable validation (default: True)
        """
        self.logger = get_logger("triplet_extractor")
        self.config = config or {}
        self.config.update(kwargs)
        self.progress_tracker = get_progress_tracker()
        # Ensure progress tracker is enabled
        if not self.progress_tracker.enabled:
            self.progress_tracker.enabled = True

        # Store parameters
        self.include_temporal = include_temporal
        self.include_provenance = include_provenance

        # Method configuration
        self.method = method if isinstance(method, list) else [method]
        self.min_confidence = self.config.get("min_confidence", 0.5)
        self.validate_triplets = self.config.get("validate", True)

        self.triplet_validator = TripletValidator(**self.config.get("validator", {}))
        self.rdf_serializer = RDFSerializer(**self.config.get("serializer", {}))
        self.quality_checker = TripletQualityChecker(**self.config.get("quality", {}))

        self.supported_formats = ["turtle", "ntriples", "jsonld", "xml"]

    def extract_triplets(
        self,
        text: str,
        entities: Optional[List[Entity]] = None,
        relations: Optional[List[Relation]] = None,
        **options,
    ) -> List[Triplet]:
        """
        Extract RDF triplets from text.

        Args:
            text: Input text
            entities: Pre-extracted entities (optional)
            relations: Pre-extracted relations (optional)
            **options: Extraction options

        Returns:
            list: List of extracted triplets
        """
        from .methods import get_triplet_method

        tracking_id = self.progress_tracker.start_tracking(
            module="semantic_extract",
            submodule="TripletExtractor",
            message="Extracting RDF triplets from text",
        )

        try:
            from .ner_extractor import NERExtractor
            from .relation_extractor import RelationExtractor

            # Extract entities if not provided
            if entities is None:
                self.progress_tracker.update_tracking(
                    tracking_id, message="Extracting entities..."
                )
                ner = NERExtractor(**self.config.get("ner", {}))
                entities = ner.extract_entities(text)

            # Extract relations if not provided
            if relations is None:
                self.progress_tracker.update_tracking(
                    tracking_id, message="Extracting relations..."
                )
                rel_extractor = RelationExtractor(**self.config.get("relation", {}))
                relations = rel_extractor.extract_relations(text, entities)

            # Use method-based extraction
            methods = options.get("method", self.method)
            if isinstance(methods, str):
                methods = [methods]

            # Merge config with options
            all_options = {**self.config, **options}

            # Try each method in order (fallback chain)
            all_triplets = []
            total_methods = len(methods)
            if total_methods <= 10:
                method_update_interval = 1  # Update every method for small datasets
            else:
                method_update_interval = max(1, min(5, total_methods // 20))
            
            # Initial progress update for methods
            remaining_methods = total_methods
            self.progress_tracker.update_progress(
                tracking_id,
                processed=0,
                total=total_methods,
                message=f"Starting triplet extraction... 0/{total_methods} methods (remaining: {remaining_methods})"
            )
            
            for method_idx, method_name in enumerate(methods, 1):
                try:
                    remaining_methods = total_methods - method_idx
                    self.progress_tracker.update_progress(
                        tracking_id,
                        processed=method_idx,
                        total=total_methods,
                        message=f"Extracting triplets using {method_name}... ({method_idx}/{total_methods}, remaining: {remaining_methods} methods)"
                    )
                    method_func = get_triplet_method(method_name)

                    # Prepare method-specific options
                    method_options = all_options.copy()
                    if method_name == "huggingface":
                        method_options["model"] = all_options.get(
                            "huggingface_model", all_options.get("model")
                        )
                        method_options["device"] = all_options.get("device")
                    elif method_name == "llm":
                        method_options["provider"] = all_options.get(
                            "provider", "openai"
                        )
                        method_options["model"] = all_options.get(
                            "llm_model", all_options.get("model")
                        )

                    triplets = method_func(
                        text,
                        entities=entities,
                        relations=relations,
                        **method_options,
                    )

                    # Filter by confidence
                    min_conf = options.get("min_confidence", self.min_confidence)
                    filtered = [t for t in triplets if t.confidence >= min_conf]

                    if filtered:
                        all_triplets.append((method_name, filtered))

                        # If not using ensemble, return first successful result
                        if len(methods) == 1:
                            result = filtered
                            if options.get("validate", self.validate_triplets):
                                result = self.triplet_validator.validate_triplets(result)
                            self.progress_tracker.stop_tracking(
                                tracking_id,
                                status="completed",
                                message=f"Extracted {len(result)} triplets using {method_name}",
                            )
                            return result

                except Exception as e:
                    self.logger.warning(f"Method {method_name} failed: {e}")
                    continue

            # Use first successful method or fallback to relation conversion
            if all_triplets:
                triplets = all_triplets[0][1]
            else:
                # Fallback: Convert relations to triplets
                self.progress_tracker.update_tracking(
                    tracking_id,
                    message=f"Converting {len(relations)} relations to triplets...",
                )
                triplets = []
                for relation in relations:
                    triplet = Triplet(
                        subject=self._format_uri(relation.subject.text),
                        predicate=self._format_uri(relation.predicate),
                        object=self._format_uri(relation.object.text),
                        confidence=relation.confidence,
                        metadata={"context": relation.context, **relation.metadata},
                    )
                    triplets.append(triplet)

            # Validate triplets
            if options.get("validate", self.validate_triplets):
                self.progress_tracker.update_tracking(
                    tracking_id, message="Validating triplets..."
                )
                triplets = self.triplet_validator.validate_triplets(triplets)

            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Extracted {len(triplets)} triplets",
            )
            return triplets

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def _format_uri(self, value: str) -> str:
        """Format value as URI."""
        # Simple URI formatting
        if value.startswith("http://") or value.startswith("https://"):
            return value

        # Format as local URI
        formatted = quote(value.replace(" ", "_"), safe="")
        return f"http://example.org/{formatted}"

    def validate_triplets(self, triplets: List[Triplet], **criteria) -> List[Triplet]:
        """
        Validate triplet quality and consistency.

        Args:
            triplets: List of triplets
            **criteria: Validation criteria

        Returns:
            list: Validated triplets
        """
        return self.triplet_validator.validate_triplets(triplets, **criteria)

    def serialize_triplets(
        self, triplets: List[Triplet], format: str = "turtle", **options
    ) -> str:
        """
        Serialize triplets to RDF format.

        Args:
            triplets: List of triplets
            format: RDF format (turtle, ntriples, jsonld, xml)
            **options: Serialization options

        Returns:
            str: Serialized RDF
        """
        return self.rdf_serializer.serialize_to_rdf(triplets, format, **options)

    def process_batch(self, texts: List[str], **options) -> List[List[Triplet]]:
        """
        Process multiple texts for triplet extraction.

        Args:
            texts: List of input texts
            **options: Processing options

        Returns:
            list: List of triplet lists for each text
        """
        return [self.extract_triplets(text, **options) for text in texts]


class TripletValidator:
    """Triplet validation engine."""

    def __init__(self, **config):
        """Initialize triplet validator."""
        self.logger = get_logger("triplet_validator")
        self.config = config

    def validate_triplet(self, triplet: Triplet, **criteria) -> bool:
        """
        Validate individual triplet.

        Args:
            triplet: Triplet to validate
            **criteria: Validation criteria

        Returns:
            bool: True if valid
        """
        # Check structure
        if not triplet.subject or not triplet.predicate or not triplet.object:
            return False

        # Check confidence
        min_confidence = criteria.get("min_confidence", 0.5)
        if triplet.confidence < min_confidence:
            return False

        return True

    def validate_triplets(self, triplets: List[Triplet], **criteria) -> List[Triplet]:
        """
        Validate list of triplets.

        Args:
            triplets: List of triplets
            **criteria: Validation criteria

        Returns:
            list: Valid triplets
        """
        return [t for t in triplets if self.validate_triplet(t, **criteria)]

    def check_triplet_consistency(self, triplets: List[Triplet]) -> Dict[str, Any]:
        """
        Check consistency among triplets.

        Args:
            triplets: List of triplets

        Returns:
            dict: Consistency report
        """
        issues = []

        # Check for contradictory triplets
        # (simplified - would need domain knowledge for full implementation)

        return {
            "total_triplets": len(triplets),
            "issues": issues,
            "consistent": len(issues) == 0,
        }


class RDFSerializer:
    """RDF serialization handler."""

    def __init__(self, **config):
        """Initialize RDF serializer."""
        self.logger = get_logger("rdf_serializer")
        self.config = config

    def serialize_to_rdf(
        self, triplets: List[Triplet], format: str = "turtle", **options
    ) -> str:
        """
        Serialize triplets to RDF format.

        Args:
            triplets: List of triplets
            format: RDF format
            **options: Serialization options

        Returns:
            str: Serialized RDF
        """
        if format == "turtle":
            return self._serialize_turtle(triplets, **options)
        elif format == "ntriples":
            return self._serialize_ntriples(triplets, **options)
        elif format == "jsonld":
            return self._serialize_jsonld(triplets, **options)
        elif format == "xml":
            return self._serialize_xml(triplets, **options)
        else:
            raise ValidationError(f"Unsupported RDF format: {format}")

    def _serialize_turtle(self, triplets: List[Triplet], **options) -> str:
        """Serialize to Turtle format."""
        lines = ["@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ."]

        for triplet in triplets:
            line = f"{triplet.subject} <{triplet.predicate}> {triplet.object} ."
            lines.append(line)

        return "\n".join(lines)

    def _serialize_ntriples(self, triplets: List[Triplet], **options) -> str:
        """Serialize to N-Triples format."""
        lines = []
        for triplet in triplets:
            line = f"<{triplet.subject}> <{triplet.predicate}> <{triplet.object}> ."
            lines.append(line)
        return "\n".join(lines)

    def _serialize_jsonld(self, triplets: List[Triplet], **options) -> str:
        """Serialize to JSON-LD format."""
        import json

        graph = []
        for triplet in triplets:
            graph.append({"@id": triplet.subject, triplet.predicate: triplet.object})

        return json.dumps({"@graph": graph}, indent=2)

    def _serialize_xml(self, triplets: List[Triplet], **options) -> str:
        """Serialize to RDF/XML format."""
        lines = [
            '<?xml version="1.0"?>',
            '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">',
        ]

        for triplet in triplets:
            lines.append(f'  <rdf:Description rdf:about="{triplet.subject}">')
            lines.append(
                f"    <{triplet.predicate}>{triplet.object}</{triplet.predicate}>"
            )
            lines.append("  </rdf:Description>")

        lines.append("</rdf:RDF>")
        return "\n".join(lines)


class TripletQualityChecker:
    """Triplet quality assessment engine."""

    def __init__(self, **config):
        """Initialize triplet quality checker."""
        self.logger = get_logger("triplet_quality_checker")
        self.config = config

    def assess_triplet_quality(self, triplet: Triplet, **metrics) -> Dict[str, Any]:
        """
        Assess quality of individual triplet.

        Args:
            triplet: Triplet to assess
            **metrics: Quality metrics

        Returns:
            dict: Quality assessment
        """
        return {
            "confidence": triplet.confidence,
            "completeness": 1.0
            if triplet.subject and triplet.predicate and triplet.object
            else 0.0,
            "quality_score": triplet.confidence,
        }

    def calculate_quality_scores(
        self, triplets: List[Triplet], **options
    ) -> Dict[str, Any]:
        """
        Calculate quality scores for triplets.

        Args:
            triplets: List of triplets
            **options: Quality options

        Returns:
            dict: Quality scores
        """
        if not triplets:
            return {}

        scores = [self.assess_triplet_quality(t)["quality_score"] for t in triplets]

        return {
            "average_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "high_quality": len([s for s in scores if s >= 0.8]),
            "medium_quality": len([s for s in scores if 0.5 <= s < 0.8]),
            "low_quality": len([s for s in scores if s < 0.5]),
        }
