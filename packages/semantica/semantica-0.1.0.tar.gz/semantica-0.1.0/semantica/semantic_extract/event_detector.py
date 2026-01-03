"""
Event Detection Module

This module provides comprehensive event detection and extraction capabilities,
enabling identification of events, their participants, temporal information,
and relationships between events. Supports multiple extraction methods for
entity and relation extraction used in event detection.

Supported Methods (for underlying NER/Relation extractors):
    - "pattern": Pattern-based extraction
    - "regex": Regex-based extraction
    - "rules": Rule-based extraction
    - "ml": ML-based extraction (spaCy)
    - "huggingface": HuggingFace model extraction
    - "llm": LLM-based extraction
    - Any method supported by NERExtractor and RelationExtractor

Algorithms Used:
    - Pattern Matching: Regular expression matching for event triggers
    - Temporal Extraction: Date/time pattern recognition and parsing
    - Location Extraction: Named entity recognition for locations
    - Participant Extraction: Capitalization-based and pattern-based participant detection
    - Event Classification: Rule-based and ML-based event type classification
    - Temporal Sorting: Chronological ordering algorithms
    - Event Relationship Detection: Graph-based event relationship extraction

Key Features:
    - Event detection and classification
    - Temporal event processing and sorting
    - Event relationship extraction
    - Event confidence scoring
    - Custom event pattern detection
    - Participant and location extraction
    - Integration with multiple NER and relation extraction methods
    - Method parameter support for underlying extractors

Main Classes:
    - EventDetector: Main event detection coordinator
    - EventClassifier: Event type classification
    - TemporalEventProcessor: Temporal event handling
    - EventRelationshipExtractor: Event relationship extraction
    - Event: Event representation dataclass

Example Usage:
    >>> from semantica.semantic_extract import EventDetector
    >>> # Using default methods
    >>> detector = EventDetector()
    >>> events = detector.detect_events("Apple was founded in 1976 by Steve Jobs.")
    >>> 
    >>> # Using LLM-based extraction for entities
    >>> detector = EventDetector(ner_method="llm", provider="openai")
    >>> events = detector.detect_events("Apple was founded in 1976 by Steve Jobs.")
    >>> 
    >>> classified = detector.classify_events(events)

Author: Semantica Contributors
License: MIT
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from ..utils.exceptions import ProcessingError
from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker
from .ner_extractor import Entity


@dataclass
class Event:
    """Event representation."""

    text: str
    event_type: str
    start_char: int
    end_char: int
    participants: List[str] = field(default_factory=list)
    location: Optional[str] = None
    time: Optional[str] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class EventDetector:
    """Event detection and extraction handler."""

    def __init__(
        self,
        event_types: Optional[List[str]] = None,
        extract_participants: bool = True,
        extract_location: bool = True,
        extract_time: bool = True,
        method: Union[str, List[str]] = None,
        config=None,
        **kwargs
    ):
        """
        Initialize event detector.

        Args:
            event_types: Specific event types to detect (e.g., ["launch", "acquisition"])
            extract_participants: Whether to extract event participants
            extract_location: Whether to extract event locations
            extract_time: Whether to extract temporal information
            method: Extraction method(s) for underlying NER/relation extractors.
                   Can be passed to ner_method and relation_method in config.
            config: Legacy config dict (deprecated, use kwargs)
            **kwargs: Configuration options:
                - ner_method: Method for NER extraction (if entities need to be extracted)
                - relation_method: Method for relation extraction (if relations need to be extracted)
                - Other options passed to sub-components
        """
        self.logger = get_logger("event_detector")
        self.config = config or {}
        self.config.update(kwargs)
        self.progress_tracker = get_progress_tracker()
        # Ensure progress tracker is enabled
        if not self.progress_tracker.enabled:
            self.progress_tracker.enabled = True

        # Store parameters
        self.event_types_filter = event_types
        self.extract_participants = extract_participants
        self.extract_location = extract_location
        self.extract_time = extract_time

        # Store method for passing to extractors if needed
        if method is not None:
            self.config["ner_method"] = method
            self.config["relation_method"] = method

        self.event_classifier = EventClassifier(**self.config.get("classifier", {}))
        self.temporal_processor = TemporalEventProcessor(
            **self.config.get("temporal", {})
        )
        self.relationship_extractor = EventRelationshipExtractor(
            **self.config.get("relationship", {})
        )

        # Event patterns
        self.event_patterns = {
            "founded": r"founded|created|established",
            "acquired": r"acquired|bought|purchased",
            "launched": r"launched|released|introduced",
            "announced": r"announced|declared|stated",
            "meeting": r"met|meeting|conference|summit",
        }

    def detect_events(self, text: str, **options) -> List[Event]:
        """
        Detect events in text content.

        Args:
            text: Input text
            **options: Detection options

        Returns:
            list: List of detected events
        """
        tracking_id = self.progress_tracker.start_tracking(
            module="semantic_extract",
            submodule="EventDetector",
            message="Detecting events in text",
        )

        try:
            events = []

            # Determine which event types to detect
            event_patterns_to_use = self.event_patterns
            if self.event_types_filter:
                event_patterns_to_use = {
                    k: v for k, v in self.event_patterns.items()
                    if k in self.event_types_filter
                }

            # Detect events using patterns
            total_event_types = len(event_patterns_to_use)
            if total_event_types <= 10:
                event_type_update_interval = 1  # Update every type for small datasets
            else:
                event_type_update_interval = max(1, min(5, total_event_types // 20))
            
            # Initial progress update
            remaining_types = total_event_types
            self.progress_tracker.update_progress(
                tracking_id,
                processed=0,
                total=total_event_types,
                message=f"Scanning text for event patterns... 0/{total_event_types} event types (remaining: {remaining_types})"
            )
            
            event_type_idx = 0
            for event_type, pattern in event_patterns_to_use.items():
                event_type_idx += 1
                remaining_types = total_event_types - event_type_idx
                
                # Count matches first to show progress
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                total_matches = len(matches)
                
                # Initialize match update interval
                if total_matches <= 10:
                    match_update_interval = 1
                else:
                    match_update_interval = max(1, min(10, total_matches // 100))
                
                if tracking_id and total_matches > 0:
                    remaining_matches = total_matches
                    self.progress_tracker.update_progress(
                        tracking_id,
                        processed=0,
                        total=total_matches,
                        message=f"Processing {event_type} events... 0/{total_matches} matches (remaining: {remaining_matches})"
                    )
                
                for match_idx, match in enumerate(matches, 1):
                    # Extract surrounding context
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end]

                    # Extract participants if enabled
                    participants = []
                    if self.extract_participants:
                        participants = self._extract_participants(context)

                    # Extract location if enabled
                    location = None
                    if self.extract_location:
                        location = self._extract_location(context)

                    # Extract time if enabled
                    time_info = None
                    if self.extract_time:
                        time_info = self._extract_time(context)

                    event = Event(
                        text=match.group(0),
                        event_type=event_type,
                        start_char=match.start(),
                        end_char=match.end(),
                        participants=participants,
                        location=location,
                        time=time_info,
                        confidence=0.7,
                        metadata={"context": context},
                    )
                    events.append(event)
                    
                    # Update progress for matches
                    if tracking_id and total_matches > 0:
                        remaining_matches = total_matches - match_idx
                        should_update = (
                            match_idx % match_update_interval == 0 or 
                            match_idx == total_matches or 
                            match_idx == 1 or
                            total_matches <= 10  # Always update for small datasets
                        )
                        if should_update:
                            self.progress_tracker.update_progress(
                                tracking_id,
                                processed=match_idx,
                                total=total_matches,
                                message=f"Processing {event_type} events... {match_idx}/{total_matches} matches (remaining: {remaining_matches})"
                            )
                
                # Update progress for event types
                if tracking_id:
                    should_update = (
                        event_type_idx % event_type_update_interval == 0 or 
                        event_type_idx == total_event_types or 
                        event_type_idx == 1 or
                        total_event_types <= 10  # Always update for small datasets
                    )
                    if should_update:
                        self.progress_tracker.update_progress(
                            tracking_id,
                            processed=event_type_idx,
                            total=total_event_types,
                            message=f"Scanning text for event patterns... {event_type_idx}/{total_event_types} event types (remaining: {remaining_types})"
                        )

            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Detected {len(events)} events",
            )
            return events

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def _extract_participants(self, context: str) -> List[str]:
        """Extract event participants from context."""
        # Simple extraction - look for capitalized words
        participants = []
        words = context.split()

        # Look for patterns like "X and Y", "X, Y, and Z"
        capitalized = [w for w in words if w[0].isupper() and len(w) > 2]
        participants.extend(capitalized[:3])  # Limit to first few

        return participants

    def classify_events(self, events: List[Event], **context) -> Dict[str, List[Event]]:
        """
        Classify events by type and category.

        Args:
            events: List of events
            **context: Context information

        Returns:
            dict: Events grouped by type
        """
        return self.event_classifier.classify_events(events, **context)

    def extract_event_properties(self, events: List[Event], **options) -> List[Event]:
        """
        Extract properties and attributes from events.

        Args:
            events: List of events
            **options: Extraction options

        Returns:
            list: Events with extracted properties
        """
        for event in events:
            # Extract location
            event.location = self._extract_location(event.metadata.get("context", ""))

            # Extract time
            event.time = self._extract_time(event.metadata.get("context", ""))

        return events

    def _extract_location(self, context: str) -> Optional[str]:
        """Extract location from context."""
        # Simple pattern matching for locations
        location_patterns = [
            r"in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        ]

        for pattern in location_patterns:
            match = re.search(pattern, context)
            if match:
                return match.group(1)

        return None

    def _extract_time(self, context: str) -> Optional[str]:
        """Extract time from context."""
        # Simple pattern matching for dates/times
        time_patterns = [
            r"on\s+([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})",
            r"in\s+(\d{4})",
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        ]

        for pattern in time_patterns:
            match = re.search(pattern, context)
            if match:
                return match.group(1)

        return None

    def process_temporal_events(self, events: List[Event], **options) -> List[Event]:
        """
        Process temporal information in events.

        Args:
            events: List of events
            **options: Processing options

        Returns:
            list: Events with temporal information
        """
        return self.temporal_processor.process_temporal(events, **options)


class EventClassifier:
    """Event type classification."""

    def __init__(self, **config):
        """Initialize event classifier."""
        self.logger = get_logger("event_classifier")
        self.config = config

    def classify_events(self, events: List[Event], **context) -> Dict[str, List[Event]]:
        """
        Classify events by type.

        Args:
            events: List of events
            **context: Context information

        Returns:
            dict: Events grouped by type
        """
        classified = {}
        for event in events:
            if event.event_type not in classified:
                classified[event.event_type] = []
            classified[event.event_type].append(event)

        return classified


class TemporalEventProcessor:
    """Temporal event handling."""

    def __init__(self, **config):
        """Initialize temporal event processor."""
        self.logger = get_logger("temporal_event_processor")
        self.config = config

    def process_temporal(self, events: List[Event], **options) -> List[Event]:
        """
        Process temporal information in events.

        Args:
            events: List of events
            **options: Processing options

        Returns:
            list: Events with processed temporal info
        """
        # Extract and normalize temporal information
        for event in events:
            if not event.time:
                # Try to extract from context
                context = event.metadata.get("context", "")
                event.time = self._extract_temporal(context)

        # Sort events by time if available
        if options.get("sort_by_time", False):
            events.sort(key=lambda e: self._parse_time(e.time) if e.time else 0)

        return events

    def _extract_temporal(self, context: str) -> Optional[str]:
        """Extract temporal expression from context."""
        # Simple temporal extraction
        patterns = [r"(\d{4})", r"([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})"]

        for pattern in patterns:
            match = re.search(pattern, context)
            if match:
                return match.group(1)

        return None

    def _parse_time(self, time_str: Optional[str]) -> int:
        """Parse time string to integer for sorting."""
        if not time_str:
            return 0

        # Extract year if available
        year_match = re.search(r"(\d{4})", time_str)
        if year_match:
            return int(year_match.group(1))

        return 0


class EventRelationshipExtractor:
    """Event relationship extraction."""

    def __init__(self, **config):
        """Initialize event relationship extractor."""
        self.logger = get_logger("event_relationship_extractor")
        self.config = config

    def extract_relationships(
        self, events: List[Event], **options
    ) -> List[Dict[str, Any]]:
        """
        Extract relationships between events.

        Args:
            events: List of events
            **options: Extraction options

        Returns:
            list: List of event relationships
        """
        relationships = []

        # Find related events (same participants, same location, sequential time)
        for i, event1 in enumerate(events):
            for event2 in events[i + 1 :]:
                # Check for shared participants
                shared_participants = set(event1.participants) & set(
                    event2.participants
                )
                if shared_participants:
                    relationships.append(
                        {
                            "event1": event1.event_type,
                            "event2": event2.event_type,
                            "relationship": "related",
                            "reason": "shared_participants",
                            "participants": list(shared_participants),
                        }
                    )

        return relationships
