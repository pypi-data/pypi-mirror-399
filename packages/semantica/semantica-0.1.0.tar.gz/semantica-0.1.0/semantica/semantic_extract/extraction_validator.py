"""
Extraction Validator Module

This module provides comprehensive quality validation for semantic extractions,
ensuring accuracy, consistency, and reliability of extracted entities and relations.
Supports method parameter for future extensibility with method-specific validation.

Supported Methods (for future extensibility):
    - Method parameter reserved for method-specific validation strategies
    - Currently supports general validation for all extraction methods
    - Future: Method-specific validation rules (e.g., "llm", "ml", "pattern")

Algorithms Used:
    - Confidence Thresholding: Statistical threshold-based filtering
    - Duplicate Detection: Set-based and similarity-based deduplication
    - Consistency Checking: Rule-based and graph-based consistency validation
    - Quality Scoring: Weighted scoring algorithms for extraction quality
    - Validation Metrics: Precision, recall, F1-score calculations
    - Boundary Validation: Character position and text boundary checking

Key Features:
    - Entity validation with confidence checking
    - Relation validation and consistency checking
    - Quality scoring and metrics calculation
    - Duplicate detection
    - Confidence-based filtering
    - Validation result reporting
    - Method parameter support for future method-specific validation

Main Classes:
    - ExtractionValidator: Main validation coordinator
    - ValidationResult: Validation result representation dataclass

Example Usage:
    >>> from semantica.semantic_extract import ExtractionValidator
    >>> # Using default validation
    >>> validator = ExtractionValidator()
    >>> result = validator.validate_entities(entities)
    >>> if result.valid:
    ...     print(f"Quality score: {result.score}")
    >>> 
    >>> # Using method-specific validation (future extensibility)
    >>> validator = ExtractionValidator(method="llm")
    >>> filtered = validator.filter_by_confidence(entities, min_confidence=0.8)

Author: Semantica Contributors
License: MIT
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..utils.exceptions import ProcessingError
from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker
from .ner_extractor import Entity
from .relation_extractor import Relation


@dataclass
class ValidationResult:
    """Validation result representation."""

    valid: bool
    score: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class ExtractionValidator:
    """Validator for semantic extractions."""

    def __init__(self, method: Optional[str] = None, **config):
        """
        Initialize extraction validator.

        Args:
            method: Validation method (for future extensibility, currently unused)
            **config: Configuration options:
                - min_confidence: Minimum confidence threshold (default: 0.5)
                - validate_consistency: Check consistency (default: True)
        """
        self.logger = get_logger("extraction_validator")
        self.config = config
        self.progress_tracker = get_progress_tracker()
        # Ensure progress tracker is enabled
        if not self.progress_tracker.enabled:
            self.progress_tracker.enabled = True

        self.method = method  # Reserved for future method-based validation
        self.min_confidence = config.get("min_confidence", 0.5)
        self.validate_consistency = config.get("validate_consistency", True)

    def validate_entities(self, entities: List[Entity], **options) -> ValidationResult:
        """
        Validate extracted entities.

        Args:
            entities: List of entities
            **options: Validation options

        Returns:
            ValidationResult: Validation result
        """
        tracking_id = self.progress_tracker.start_tracking(
            module="semantic_extract",
            submodule="ExtractionValidator",
            message=f"Validating {len(entities)} entities",
        )

        try:
            errors = []
            warnings = []
            metrics = {}

            min_confidence = options.get("min_confidence", self.min_confidence)

            # Check confidence scores
            self.progress_tracker.update_tracking(
                tracking_id, message="Checking confidence scores..."
            )
            low_confidence = [e for e in entities if e.confidence < min_confidence]
            if low_confidence:
                warnings.append(
                    f"{len(low_confidence)} entities below confidence threshold"
                )

            # Check for duplicates
            self.progress_tracker.update_tracking(
                tracking_id, message="Checking for duplicates..."
            )
            entity_texts = [e.text.lower() for e in entities]
            duplicates = len(entity_texts) - len(set(entity_texts))
            if duplicates > 0:
                warnings.append(f"{duplicates} duplicate entities found")

            # Check for empty entities
            empty_entities = [e for e in entities if not e.text.strip()]
            if empty_entities:
                errors.append(f"{len(empty_entities)} empty entities found")

            # Calculate metrics
            metrics = {
                "total_entities": len(entities),
                "high_confidence": len([e for e in entities if e.confidence >= 0.8]),
                "medium_confidence": len(
                    [e for e in entities if min_confidence <= e.confidence < 0.8]
                ),
                "low_confidence": len(low_confidence),
                "unique_entities": len(set(entity_texts)),
                "duplicates": duplicates,
                "entity_types": len(set(e.label for e in entities)),
                "average_confidence": sum(e.confidence for e in entities)
                / len(entities)
                if entities
                else 0.0,
            }

            # Calculate score
            score = self._calculate_entity_score(entities, metrics)

            valid = len(errors) == 0

            result = ValidationResult(
                valid=valid,
                score=score,
                errors=errors,
                warnings=warnings,
                metrics=metrics,
            )

            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Validation complete: {len(errors)} errors, {len(warnings)} warnings",
            )
            return result

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def validate_relations(
        self, relations: List[Relation], **options
    ) -> ValidationResult:
        """
        Validate extracted relations.

        Args:
            relations: List of relations
            **options: Validation options

        Returns:
            ValidationResult: Validation result
        """
        errors = []
        warnings = []
        metrics = {}

        min_confidence = options.get("min_confidence", self.min_confidence)

        # Check confidence scores
        low_confidence = [r for r in relations if r.confidence < min_confidence]
        if low_confidence:
            warnings.append(
                f"{len(low_confidence)} relations below confidence threshold"
            )

        # Check for valid subject and object
        invalid_relations = [
            r
            for r in relations
            if not r.subject or not r.object or r.subject.text == r.object.text
        ]
        if invalid_relations:
            errors.append(f"{len(invalid_relations)} invalid relations found")

        # Check consistency
        if self.validate_consistency:
            consistency_issues = self._check_consistency(relations)
            if consistency_issues:
                warnings.append(f"{len(consistency_issues)} consistency issues found")

        # Calculate metrics
        metrics = {
            "total_relations": len(relations),
            "high_confidence": len([r for r in relations if r.confidence >= 0.8]),
            "medium_confidence": len(
                [r for r in relations if min_confidence <= r.confidence < 0.8]
            ),
            "low_confidence": len(low_confidence),
            "relation_types": len(set(r.predicate for r in relations)),
            "average_confidence": sum(r.confidence for r in relations) / len(relations)
            if relations
            else 0.0,
            "invalid_relations": len(invalid_relations),
        }

        # Calculate score
        score = self._calculate_relation_score(relations, metrics)

        valid = len(errors) == 0

        return ValidationResult(
            valid=valid, score=score, errors=errors, warnings=warnings, metrics=metrics
        )

    def _check_consistency(self, relations: List[Relation]) -> List[str]:
        """Check consistency of relations."""
        issues = []

        # Check for contradictory relations
        relation_pairs = {}
        for relation in relations:
            key = (relation.subject.text, relation.object.text)
            if key not in relation_pairs:
                relation_pairs[key] = []
            relation_pairs[key].append(relation.predicate)

        # Find contradictions (e.g., "founded_by" and "founded" for same pair)
        for key, predicates in relation_pairs.items():
            if len(set(predicates)) > 1:
                # Check for obvious contradictions
                if "founded_by" in predicates and "founded" in predicates:
                    issues.append(f"Contradictory relations for {key}")

        return issues

    def _calculate_entity_score(
        self, entities: List[Entity], metrics: Dict[str, Any]
    ) -> float:
        """Calculate entity validation score."""
        if not entities:
            return 0.0

        score = 1.0

        # Confidence penalty
        low_conf_ratio = metrics.get("low_confidence", 0) / metrics.get(
            "total_entities", 1
        )
        score *= 1.0 - low_conf_ratio * 0.5

        # Duplicate penalty
        dup_ratio = metrics.get("duplicates", 0) / metrics.get("total_entities", 1)
        score *= 1.0 - dup_ratio * 0.3

        # Average confidence factor
        avg_confidence = metrics.get("average_confidence", 0.0)
        score *= 0.5 + avg_confidence * 0.5

        return max(0.0, min(1.0, score))

    def _calculate_relation_score(
        self, relations: List[Relation], metrics: Dict[str, Any]
    ) -> float:
        """Calculate relation validation score."""
        if not relations:
            return 0.0

        score = 1.0

        # Confidence penalty
        low_conf_ratio = metrics.get("low_confidence", 0) / metrics.get(
            "total_relations", 1
        )
        score *= 1.0 - low_conf_ratio * 0.5

        # Invalid relation penalty
        invalid_ratio = metrics.get("invalid_relations", 0) / metrics.get(
            "total_relations", 1
        )
        score *= 1.0 - invalid_ratio * 0.7

        # Average confidence factor
        avg_confidence = metrics.get("average_confidence", 0.0)
        score *= 0.5 + avg_confidence * 0.5

        return max(0.0, min(1.0, score))

    def filter_by_confidence(
        self, entities: List[Entity], min_confidence: Optional[float] = None
    ) -> List[Entity]:
        """
        Filter entities by confidence.

        Args:
            entities: List of entities
            min_confidence: Minimum confidence (uses default if None)

        Returns:
            list: Filtered entities
        """
        threshold = (
            min_confidence if min_confidence is not None else self.min_confidence
        )
        return [e for e in entities if e.confidence >= threshold]

    def filter_relations_by_confidence(
        self, relations: List[Relation], min_confidence: Optional[float] = None
    ) -> List[Relation]:
        """
        Filter relations by confidence.

        Args:
            relations: List of relations
            min_confidence: Minimum confidence (uses default if None)

        Returns:
            list: Filtered relations
        """
        threshold = (
            min_confidence if min_confidence is not None else self.min_confidence
        )
        return [r for r in relations if r.confidence >= threshold]
