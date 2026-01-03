"""
Named Entity Recognition Extractor Module

This module provides comprehensive NER capabilities with multiple extraction methods,
ranging from simple pattern matching to advanced LLM-based extraction, with support
for fallback chains and ensemble voting.

Supported Methods:
    - "pattern": Pattern-based extraction using simple regex patterns
    - "regex": Advanced regex-based extraction with custom patterns
    - "rules": Rule-based extraction using linguistic rules
    - "ml": ML-based extraction using spaCy (default)
    - "huggingface": Custom HuggingFace NER models
    - "llm": LLM-based extraction using various providers (OpenAI, Gemini, Groq, etc.)

Algorithms Used:
    - Regular Expression Matching: Pattern matching using finite automata
    - Rule-based Extraction: Linguistic rule application and pattern matching
    - Neural Named Entity Recognition: spaCy's CNN/Transformer-based NER models
    - Transformer Models: BERT, RoBERTa, DistilBERT for token classification
    - Large Language Models: GPT, Claude, Gemini for zero-shot/few-shot extraction
    - Ensemble Voting: Majority voting and confidence-weighted aggregation
    - Deduplication: Set-based and similarity-based entity deduplication

Key Features:
    - Multiple extraction methods:
        * Pattern-based: Simple regex pattern matching
        * Regex-based: Advanced regex with custom patterns
        * Rules-based: Linguistic rule-based extraction
        * ML-based: spaCy-based machine learning extraction (default)
        * HuggingFace: Custom HuggingFace NER models
        * LLM-based: Large language model extraction
    - Fallback chain support: Try methods in order until one succeeds
    - Ensemble voting: Combine results from multiple methods
    - Post-processing: Entity boundary validation and deduplication
    - Multiple entity type support (PERSON, ORG, GPE, DATE, etc.)
    - Confidence scoring and filtering
    - Batch processing capabilities
    - Entity classification and grouping

Main Classes:
    - NERExtractor: Core NER extractor with method selection
    - Entity: Entity representation dataclass

Example Usage:
    >>> from semantica.semantic_extract import NERExtractor
    >>> # Using ML method (default)
    >>> extractor = NERExtractor(method="ml", model="en_core_web_sm")
    >>> entities = extractor.extract_entities("Apple Inc. was founded in 1976.")
    >>> 
    >>> # Using LLM method
    >>> extractor = NERExtractor(method="llm", provider="openai", llm_model="gpt-4")
    >>> entities = extractor.extract_entities("Apple Inc. was founded in 1976.")
    >>> 
    >>> # Using HuggingFace model
    >>> extractor = NERExtractor(method="huggingface", huggingface_model="dslim/bert-base-NER")
    >>> entities = extractor.extract_entities("Apple Inc. was founded in 1976.")
    >>> 
    >>> # Using fallback chain
    >>> extractor = NERExtractor(method=["llm", "ml", "pattern"], ensemble_voting=True)
    >>> entities = extractor.extract_entities("Apple Inc. was founded in 1976.")

Author: Semantica Contributors
License: MIT
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from ..utils.exceptions import ProcessingError
from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker

try:
    import spacy

    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


@dataclass
class Entity:
    """Entity representation."""

    text: str
    label: str
    start_char: int
    end_char: int
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class NERExtractor:
    """Named Entity Recognition extractor."""

    def __init__(self, method: Union[str, List[str]] = "ml", **config):
        """
        Initialize NER extractor.

        Args:
            method: Extraction method(s). Can be:
                - "pattern": Pattern-based extraction
                - "regex": Regex-based extraction
                - "rules": Rule-based extraction
                - "ml": ML-based (spaCy) - default
                - "huggingface": HuggingFace model
                - "llm": LLM-based extraction
                - List of methods for fallback chain
            **config: Configuration options:
                - model: Model name (for ML/HuggingFace methods)
                - huggingface_model: HuggingFace model name
                - provider: LLM provider (for LLM method)
                - llm_model: LLM model name
                - device: Device for HuggingFace models ("cuda" or "cpu")
                - min_confidence: Minimum confidence threshold
                - ensemble_voting: Enable ensemble voting (default: False)
                - post_process: Enable post-processing (default: False)
        """
        self.logger = get_logger("ner_extractor")
        self.config = config

        # Method configuration
        self.method = method if isinstance(method, list) else [method]
        self.model_name = config.get("model", "en_core_web_sm")
        self.huggingface_model = config.get(
            "huggingface_model", config.get("model", "dslim/bert-base-NER")
        )
        self.language = config.get("language", "en")
        self.min_confidence = config.get("min_confidence", 0.5)
        self.ensemble_voting = config.get("ensemble_voting", False)
        self.post_process = config.get("post_process", False)
        self.progress_tracker = get_progress_tracker()
        # Ensure progress tracker is enabled
        if not self.progress_tracker.enabled:
            self.progress_tracker.enabled = True

        # Initialize spaCy model if ML method is used
        self.nlp = None
        if "ml" in self.method and SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load(self.model_name)
            except OSError:
                self.logger.warning(
                    f"spaCy model {self.model_name} not found. ML method will fallback."
                )

    def extract(self, text: Union[str, List[Dict[str, Any]], List[str]], **kwargs) -> Union[List[Entity], List[List[Entity]]]:
        """
        Alias for extract_entities.
        Handles both single string and list of documents.
        
        Args:
            text: Input text or list of documents
            **kwargs: Extraction options
            
        Returns:
            Union[List[Entity], List[List[Entity]]]: Extracted entities
        """
        if isinstance(text, list):
            # Handle batch extraction with progress tracking
            tracking_id = self.progress_tracker.start_tracking(
                module="semantic_extract",
                submodule="NERExtractor",
                message=f"Batch extracting entities from {len(text)} documents",
            )
            
            try:
                results = []
                total_items = len(text)
                # Update more frequently: every 1% or at least every 10 items, but always update for small datasets
                if total_items <= 10:
                    update_interval = 1  # Update every item for small datasets
                else:
                    update_interval = max(1, min(10, total_items // 100))
                
                # Initial progress update - ALWAYS show this
                remaining = total_items
                self.progress_tracker.update_progress(
                    tracking_id,
                    processed=0,
                    total=total_items,
                    message=f"Starting batch extraction... 0/{total_items} (remaining: {remaining})"
                )
                
                for idx, item in enumerate(text, 1):
                    try:
                        if isinstance(item, dict) and "content" in item:
                            results.append(self.extract_entities(item["content"], **kwargs))
                        elif isinstance(item, str):
                            results.append(self.extract_entities(item, **kwargs))
                        else:
                            # Try converting to string
                            try:
                                results.append(self.extract_entities(str(item), **kwargs))
                            except Exception:
                                results.append([])
                    except Exception:
                        results.append([])
                    
                    remaining = total_items - idx
                    # Update progress: always update for small datasets, or at intervals for large ones
                    should_update = (
                        idx % update_interval == 0 or 
                        idx == total_items or 
                        idx == 1 or
                        total_items <= 10  # Always update for small datasets
                    )
                    if should_update:
                        self.progress_tracker.update_progress(
                            tracking_id,
                            processed=idx,
                            total=total_items,
                            message=f"Processing documents... {idx}/{total_items} (remaining: {remaining})"
                        )
                
                self.progress_tracker.stop_tracking(
                    tracking_id,
                    status="completed",
                    message=f"Extracted entities from {len(results)} documents",
                )
                return results
            except Exception as e:
                self.progress_tracker.stop_tracking(
                    tracking_id, status="failed", message=str(e)
                )
                raise
        else:
            return self.extract_entities(text, **kwargs)

    def extract_entities(self, text: str, **options) -> List[Entity]:
        """
        Extract named entities from text.

        Args:
            text: Input text
            **options: Extraction options:
                - entity_types: Filter by entity types (list)
                - min_confidence: Minimum confidence threshold
                - method: Override method (if not set in __init__)

        Returns:
            list: List of extracted entities
        """
        tracking_id = self.progress_tracker.start_tracking(
            module="semantic_extract",
            submodule="NERExtractor",
            message="Extracting named entities from text",
        )

        try:
            from .methods import get_entity_method
            if not text:
                self.progress_tracker.stop_tracking(
                    tracking_id, status="completed", message="No text provided"
                )
                return []

            # Use method from options if provided, otherwise use instance method
            methods = options.get("method", self.method)
            if isinstance(methods, str):
                methods = [methods]

            min_confidence = options.get("min_confidence", self.min_confidence)
            entity_types = options.get("entity_types")

            # Merge config with options
            all_options = {**self.config, **options}

            # Try each method in order (fallback chain)
            all_entities = []
            for method_name in methods:
                try:
                    self.progress_tracker.update_tracking(
                        tracking_id,
                        message=f"Extracting entities using {method_name}...",
                    )
                    method_func = get_entity_method(method_name)

                    # Prepare method-specific options
                    method_options = all_options.copy()
                    if method_name == "huggingface":
                        method_options["model"] = all_options.get(
                            "huggingface_model", self.huggingface_model
                        )
                        method_options["device"] = all_options.get("device")
                    elif method_name == "llm":
                        method_options["provider"] = all_options.get(
                            "provider", "openai"
                        )
                        method_options["model"] = all_options.get(
                            "llm_model", all_options.get("model")
                        )
                        # Pass entity_types to LLM method so it can use them in the prompt
                        if entity_types:
                            method_options["entity_types"] = entity_types

                    entities = method_func(text, **method_options)

                    # Filter by confidence and entity types
                    filtered = [e for e in entities if e.confidence >= min_confidence]
                    if entity_types:
                        # Case-insensitive and flexible matching for entity types
                        entity_types_lower = {et.lower() for et in entity_types}
                        filtered = [
                            e for e in filtered 
                            if e.label.lower() in entity_types_lower 
                            or any(et.lower() in e.label.lower() or e.label.lower() in et.lower() 
                                   for et in entity_types)
                        ]

                    if filtered:
                        all_entities.append((method_name, filtered))

                        # If not using ensemble, return first successful result
                        if not self.ensemble_voting:
                            self.progress_tracker.stop_tracking(
                                tracking_id,
                                status="completed",
                                message=f"Extracted {len(filtered)} entities using {method_name}",
                            )
                            return filtered

                except Exception as e:
                    self.logger.warning(f"Method {method_name} failed: {e}")
                    continue

            # Ensemble voting if enabled
            if self.ensemble_voting and len(all_entities) > 1:
                entities = self._vote_entities(
                    [entities for _, entities in all_entities]
                )
            elif all_entities:
                entities = all_entities[0][1]  # Use first successful method
            else:
                entities = []

            # Post-processing if enabled
            if self.post_process and entities:
                entities = self._post_process_entities(entities, text)

            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Extracted {len(entities)} entities",
            )
            return entities

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def _vote_entities(
        self, results: List[List[Entity]], threshold: float = 0.5
    ) -> List[Entity]:
        """Vote on entities across methods."""
        entity_counts = {}
        total_methods = len(results)

        for entities in results:
            for entity in entities:
                key = (entity.text.lower(), entity.label)
                if key not in entity_counts:
                    entity_counts[key] = {"entity": entity, "score": 0.0, "count": 0}
                entity_counts[key]["score"] += entity.confidence
                entity_counts[key]["count"] += 1

        # Return entities that meet threshold
        voted = []
        for key, data in entity_counts.items():
            avg_score = data["score"] / data["count"]
            if avg_score >= threshold:
                entity = data["entity"]
                entity.confidence = avg_score
                voted.append(entity)

        return voted

    def _post_process_entities(self, entities: List[Entity], text: str) -> List[Entity]:
        """Post-process entities for refinement."""
        processed = []
        seen = set()

        for entity in entities:
            # Check boundaries
            if entity.start_char < 0 or entity.end_char > len(text):
                continue

            # Check for duplicates
            key = (entity.text.lower(), entity.label, entity.start_char)
            if key in seen:
                continue
            seen.add(key)

            # Validate entity text matches
            actual_text = text[entity.start_char : entity.end_char]
            if actual_text.lower() != entity.text.lower():
                # Try to find correct boundaries
                start = text.lower().find(
                    entity.text.lower(), max(0, entity.start_char - 10)
                )
                if start >= 0:
                    entity.start_char = start
                    entity.end_char = start + len(entity.text)

            processed.append(entity)

        return processed

    def _extract_with_spacy(
        self, text: str, min_confidence: float, entity_types: Optional[List[str]]
    ) -> List[Entity]:
        """Extract entities using spaCy."""
        entities = []

        doc = self.nlp(text)

        for ent in doc.ents:
            # Filter by entity types if specified
            if entity_types and ent.label_ not in entity_types:
                continue

            # Get confidence if available
            confidence = 1.0
            if hasattr(ent, "confidence"):
                confidence = ent.confidence
            elif hasattr(ent, "score"):
                confidence = ent.score

            if confidence >= min_confidence:
                entities.append(
                    Entity(
                        text=ent.text,
                        label=ent.label_,
                        start_char=ent.start_char,
                        end_char=ent.end_char,
                        confidence=confidence,
                        metadata={
                            "lemma": ent.lemma_ if hasattr(ent, "lemma_") else ent.text
                        },
                    )
                )

        return entities

    def _extract_fallback(self, text: str) -> List[Entity]:
        """Fallback entity extraction using simple patterns."""
        entities = []

        # Simple patterns for common entity types
        patterns = {
            "PERSON": r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b",
            "ORG": r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\s+(?:Inc|Corp|LLC|Ltd|Company))\b",
            "GPE": r"\b([A-Z][a-z]+\s*(?:City|State|Country|Nation))\b",
            "DATE": r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4})\b",
        }

        import re

        for label, pattern in patterns.items():
            for match in re.finditer(pattern, text):
                entities.append(
                    Entity(
                        text=match.group(1),
                        label=label,
                        start_char=match.start(),
                        end_char=match.end(),
                        confidence=0.7,  # Lower confidence for pattern-based
                        metadata={"extraction_method": "pattern"},
                    )
                )

        return entities

    def extract_entities_batch(self, texts: List[str], **options) -> List[List[Entity]]:
        """
        Extract entities from multiple texts.

        Args:
            texts: List of input texts
            **options: Extraction options

        Returns:
            list: List of entity lists for each text
        """
        return [self.extract_entities(text, **options) for text in texts]

    def classify_entities(self, entities: List[Entity]) -> Dict[str, List[Entity]]:
        """
        Classify entities by type.

        Args:
            entities: List of entities

        Returns:
            dict: Entities grouped by type
        """
        classified = {}
        for entity in entities:
            if entity.label not in classified:
                classified[entity.label] = []
            classified[entity.label].append(entity)

        return classified

    def filter_by_confidence(
        self, entities: List[Entity], min_confidence: float
    ) -> List[Entity]:
        """
        Filter entities by confidence score.

        Args:
            entities: List of entities
            min_confidence: Minimum confidence threshold

        Returns:
            list: Filtered entities
        """
        return [e for e in entities if e.confidence >= min_confidence]
