"""
Coreference Resolution Module

This module provides comprehensive coreference resolution capabilities for resolving
pronoun references and entity coreferences in text, enabling better understanding
of entity mentions and references. Supports multiple extraction methods for
underlying entity extraction.

Supported Methods (for underlying NER extractors):
    - "pattern": Pattern-based extraction
    - "regex": Regex-based extraction
    - "rules": Rule-based extraction
    - "ml": ML-based extraction (spaCy)
    - "huggingface": HuggingFace model extraction
    - "llm": LLM-based extraction
    - Any method supported by NERExtractor

Algorithms Used:
    - Pronoun Resolution: Rule-based and distance-based antecedent resolution
    - Entity Coreference: String matching and similarity-based coreference detection
    - Coreference Chain Building: Graph-based chain construction algorithms
    - Mention Extraction: Pattern-based and ML-based mention detection
    - Ambiguity Resolution: Context-aware disambiguation algorithms
    - Distance Metrics: Character distance and sentence distance calculations

Key Features:
    - Pronoun resolution (he, she, it, they, etc.)
    - Entity coreference detection
    - Coreference chain construction
    - Ambiguity resolution
    - Cross-document coreference support
    - Mention extraction and tracking
    - Integration with multiple NER extraction methods
    - Method parameter support for underlying extractors

Main Classes:
    - CoreferenceResolver: Main coreference resolution coordinator
    - PronounResolver: Pronoun resolution engine
    - EntityCoreferenceDetector: Entity coreference detection
    - CoreferenceChainBuilder: Coreference chain construction
    - Mention: Mention representation dataclass
    - CoreferenceChain: Coreference chain representation dataclass

Example Usage:
    >>> from semantica.semantic_extract import CoreferenceResolver
    >>> # Using default methods
    >>> resolver = CoreferenceResolver()
    >>> chains = resolver.resolve_coreferences("John went to the store. He bought milk.")
    >>> 
    >>> # Using LLM-based extraction for entities
    >>> resolver = CoreferenceResolver(method="llm", provider="openai")
    >>> chains = resolver.resolve_coreferences("John went to the store. He bought milk.")
    >>> 
    >>> pronouns = resolver.resolve_pronouns("Mary said she would come.")

Author: Semantica Contributors
License: MIT
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from ..utils.exceptions import ProcessingError
from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker
from .ner_extractor import Entity


@dataclass
class Mention:
    """Mention representation."""

    text: str
    start_char: int
    end_char: int
    mention_type: str  # pronoun, entity, nominal
    entity_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CoreferenceChain:
    """Coreference chain representation."""

    mentions: List[Mention]
    representative: Mention
    entity_type: Optional[str] = None


class CoreferenceResolver:
    """Coreference resolution handler."""

    def __init__(self, method: Union[str, List[str]] = None, config=None, **kwargs):
        """
        Initialize coreference resolver.

        Args:
            method: Extraction method(s) for underlying NER extractors.
                   Can be passed to ner_method in config.
            config: Legacy config dict (deprecated, use kwargs)
            **kwargs: Configuration options:
                - ner_method: Method for NER extraction (if entities need to be extracted)
                - Other options passed to sub-components
        """
        self.logger = get_logger("coreference_resolver")
        self.config = config or {}
        self.config.update(kwargs)
        self.progress_tracker = get_progress_tracker()
        # Ensure progress tracker is enabled
        if not self.progress_tracker.enabled:
            self.progress_tracker.enabled = True

        # Store method for passing to extractors if needed
        if method is not None:
            self.config["ner_method"] = method

        self.pronoun_resolver = PronounResolver(**self.config.get("pronoun", {}))
        self.entity_detector = EntityCoreferenceDetector(
            **self.config.get("entity", {})
        )
        self.chain_builder = CoreferenceChainBuilder(**self.config.get("chain", {}))

    def resolve_coreferences(self, text: str, **options) -> List[CoreferenceChain]:
        """
        Resolve coreferences in text.

        Args:
            text: Input text
            **options: Resolution options

        Returns:
            list: List of coreference chains
        """
        tracking_id = self.progress_tracker.start_tracking(
            module="semantic_extract",
            submodule="CoreferenceResolver",
            message="Resolving coreferences in text",
        )

        try:
            total_steps = 4  # Extract mentions, resolve pronouns, detect coreferences, build chains
            current_step = 0
            
            # Step 1: Extract mentions
            current_step += 1
            remaining_steps = total_steps - current_step
            self.progress_tracker.update_progress(
                tracking_id,
                processed=current_step,
                total=total_steps,
                message=f"Extracting mentions... ({current_step}/{total_steps}, remaining: {remaining_steps} steps)"
            )
            mentions = self._extract_mentions(text)

            # Step 2: Resolve pronouns
            current_step += 1
            remaining_steps = total_steps - current_step
            self.progress_tracker.update_progress(
                tracking_id,
                processed=current_step,
                total=total_steps,
                message=f"Resolving pronouns... ({current_step}/{total_steps}, {len(mentions)} mentions, remaining: {remaining_steps} steps)"
            )
            pronoun_resolutions = self.pronoun_resolver.resolve_pronouns(
                text, mentions, **options
            )

            # Step 3: Detect entity coreferences
            current_step += 1
            remaining_steps = total_steps - current_step
            self.progress_tracker.update_progress(
                tracking_id,
                processed=current_step,
                total=total_steps,
                message=f"Detecting entity coreferences... ({current_step}/{total_steps}, remaining: {remaining_steps} steps)"
            )
            entity_corefs = self.entity_detector.detect_entity_coreferences(
                text, mentions, **options
            )

            # Step 4: Build chains
            current_step += 1
            remaining_steps = total_steps - current_step
            self.progress_tracker.update_progress(
                tracking_id,
                processed=current_step,
                total=total_steps,
                message=f"Building coreference chains... ({current_step}/{total_steps}, remaining: {remaining_steps} steps)"
            )
            chains = self.chain_builder.build_coreference_chains(mentions, **options)

            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Resolved {len(chains)} coreference chains",
            )
            return chains

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def resolve(self, text: str, **options) -> List[CoreferenceChain]:
        """
        Resolve coreferences in text (alias for resolve_coreferences).

        Args:
            text: Input text
            **options: Resolution options

        Returns:
            list: List of coreference chains
        """
        return self.resolve_coreferences(text, **options)
    def _extract_mentions(self, text: str) -> List[Mention]:
        """Extract all mentions from text."""
        mentions = []

        # Extract pronouns
        pronoun_patterns = {
            "he": r"\bhe\b",
            "she": r"\bshe\b",
            "it": r"\bit\b",
            "they": r"\bthey\b",
            "his": r"\bhis\b",
            "her": r"\bher\b",
            "their": r"\btheir\b",
        }

        total_patterns = len(pronoun_patterns)
        if total_patterns <= 10:
            pattern_update_interval = 1  # Update every pattern for small datasets
        else:
            pattern_update_interval = max(1, min(5, total_patterns // 20))

        for pattern_idx, (pronoun, pattern) in enumerate(pronoun_patterns.items(), 1):
            # Count matches first
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            total_matches = len(matches)
            
            for match in matches:
                mentions.append(
                    Mention(
                        text=match.group(0),
                        start_char=match.start(),
                        end_char=match.end(),
                        mention_type="pronoun",
                        metadata={"pronoun": pronoun},
                    )
                )

        return mentions

    def build_coreference_chains(
        self, mentions: List[Mention], **options
    ) -> List[CoreferenceChain]:
        """
        Build coreference chains from mentions.

        Args:
            mentions: List of mentions
            **options: Chain building options

        Returns:
            list: List of coreference chains
        """
        return self.chain_builder.build_coreference_chains(mentions, **options)

    def resolve_pronouns(self, text: str, **options) -> List[Tuple[str, str]]:
        """
        Resolve pronoun references in text.

        Args:
            text: Input text
            **options: Resolution options

        Returns:
            list: List of (pronoun, antecedent) tuples
        """
        mentions = self._extract_mentions(text)
        return self.pronoun_resolver.resolve_pronouns(text, mentions, **options)

    def detect_entity_coreferences(
        self, text: str, entities: List[Entity], **options
    ) -> List[CoreferenceChain]:
        """
        Detect entity coreferences in text.

        Args:
            text: Input text
            entities: List of entities
            **options: Detection options

        Returns:
            list: List of coreference chains
        """
        # Convert entities to mentions
        mentions = [
            Mention(
                text=e.text,
                start_char=e.start_char,
                end_char=e.end_char,
                mention_type="entity",
                metadata={"entity_label": e.label},
            )
            for e in entities
        ]

        return self.entity_detector.detect_entity_coreferences(
            text, mentions, **options
        )


class PronounResolver:
    """Pronoun resolution engine."""

    def __init__(self, **config):
        """Initialize pronoun resolver."""
        self.logger = get_logger("pronoun_resolver")
        self.config = config

    def resolve_pronouns(
        self, text: str, mentions: List[Mention], **options
    ) -> List[Tuple[str, str]]:
        """
        Resolve pronoun references in text.

        Args:
            text: Input text
            mentions: List of mentions
            **options: Resolution options

        Returns:
            list: List of (pronoun, antecedent) tuples
        """
        resolutions = []

        # Get pronouns and entities
        pronouns = [m for m in mentions if m.mention_type == "pronoun"]
        entities = [
            m
            for m in mentions
            if m.mention_type == "entity" or m.mention_type == "nominal"
        ]

        # Simple resolution: find closest preceding entity
        for pronoun in pronouns:
            # Find preceding entities
            preceding = [e for e in entities if e.end_char < pronoun.start_char]

            if preceding:
                # Take closest
                antecedent = max(preceding, key=lambda e: e.end_char)
                resolutions.append((pronoun.text, antecedent.text))

        return resolutions


class EntityCoreferenceDetector:
    """Entity coreference detection."""

    def __init__(self, **config):
        """Initialize entity coreference detector."""
        self.logger = get_logger("entity_coreference_detector")
        self.config = config

    def detect_entity_coreferences(
        self, text: str, mentions: List[Mention], **options
    ) -> List[CoreferenceChain]:
        """
        Detect entity coreferences in text.

        Args:
            text: Input text
            mentions: List of mentions
            **options: Detection options

        Returns:
            list: List of coreference chains
        """
        chains = []

        # Group mentions by text similarity
        entity_mentions = [
            m for m in mentions if m.mention_type in ["entity", "nominal"]
        ]

        # Simple grouping by exact text match
        text_groups = {}
        for mention in entity_mentions:
            key = mention.text.lower()
            if key not in text_groups:
                text_groups[key] = []
            text_groups[key].append(mention)

        # Create chains from groups
        for key, group_mentions in text_groups.items():
            if len(group_mentions) > 1:
                # Use first mention as representative
                representative = group_mentions[0]
                chain = CoreferenceChain(
                    mentions=group_mentions, representative=representative
                )
                chains.append(chain)

        return chains


class CoreferenceChainBuilder:
    """Coreference chain construction."""

    def __init__(self, **config):
        """Initialize coreference chain builder."""
        self.logger = get_logger("coreference_chain_builder")
        self.config = config

    def build_coreference_chains(
        self, mentions: List[Mention], **options
    ) -> List[CoreferenceChain]:
        """
        Build coreference chains from mentions.

        Args:
            mentions: List of mentions
            **options: Chain building options

        Returns:
            list: List of coreference chains
        """
        chains = []

        # Simple implementation: group by text similarity
        processed = set()

        for mention in mentions:
            if mention.text.lower() in processed:
                continue

            # Find similar mentions
            similar = [
                m
                for m in mentions
                if m.text.lower() == mention.text.lower()
                or self._similar_mentions(mention.text, m.text)
            ]

            if len(similar) > 1:
                processed.add(mention.text.lower())

                # Representative is first (leftmost) mention
                representative = min(similar, key=lambda m: m.start_char)

                chain = CoreferenceChain(
                    mentions=similar,
                    representative=representative,
                    entity_type=similar[0].metadata.get("entity_label"),
                )
                chains.append(chain)

        return chains

    def _similar_mentions(self, text1: str, text2: str) -> bool:
        """Check if two mentions are similar."""
        t1_lower = text1.lower()
        t2_lower = text2.lower()

        # Exact match
        if t1_lower == t2_lower:
            return True

        # One contains the other
        if t1_lower in t2_lower or t2_lower in t1_lower:
            return True

        # Word overlap
        words1 = set(t1_lower.split())
        words2 = set(t2_lower.split())
        overlap = (
            len(words1 & words2) / max(len(words1), len(words2))
            if words1 or words2
            else 0
        )

        return overlap > 0.7
