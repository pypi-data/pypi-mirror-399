"""
Extraction Methods Module

This module provides all extraction methods as simple, reusable functions for
entities, relations, and triplets. It supports multiple extraction approaches
ranging from simple pattern matching to advanced LLM-based extraction.

Supported Methods:

Entity Extraction:
    - "pattern": Pattern-based entity extraction using regex
    - "regex": Advanced regex-based entity extraction with custom patterns
    - "rules": Rule-based entity extraction using linguistic rules
    - "ml": ML-based entity extraction using spaCy
    - "huggingface": HuggingFace NER model extraction
    - "llm": LLM-based entity extraction

Relation Extraction:
    - "pattern": Pattern-based relation extraction
    - "regex": Advanced regex-based relation extraction
    - "cooccurrence": Co-occurrence based relation detection
    - "dependency": Dependency parsing-based relation extraction
    - "huggingface": HuggingFace relation extraction models
    - "llm": LLM-based relation extraction

Triplet Extraction:
    - "pattern": Pattern-based triplet extraction
    - "rules": Rule-based triplet extraction
    - "huggingface": HuggingFace triplet extraction models
    - "llm": LLM-based triplet extraction

Algorithms Used:

Entity Extraction:
    - Regular Expression Matching: Finite automata-based pattern matching
    - Rule-based NLP: Linguistic rule application and pattern matching
    - Neural NER: CNN/Transformer-based named entity recognition (spaCy)
    - Transformer Token Classification: BERT/RoBERTa for token-level classification
    - LLM Generation: Transformer-based language models for entity extraction

Relation Extraction:
    - Pattern Matching: Regex and string pattern matching algorithms
    - Co-occurrence Analysis: Proximity-based entity relationship detection
    - Dependency Parsing: Transition-based and graph-based parsing algorithms
    - Sequence Classification: Transformer-based relation classification
    - LLM Generation: Language model-based relation extraction

Triplet Extraction:
    - Pattern Matching: Subject-predicate-object pattern extraction
    - Rule-based Extraction: Linguistic rule application
    - Seq2Seq Models: Encoder-decoder transformer models for triplet generation
    - LLM Generation: Structured output generation from language models

Key Features:
    - Multiple extraction methods for entities:
        * Pattern-based: Simple regex pattern matching
        * Regex-based: Advanced regex with custom patterns
        * Rules-based: Linguistic rule-based extraction
        * ML-based: spaCy-based machine learning extraction
        * HuggingFace: Custom HuggingFace NER models
        * LLM-based: Large language model extraction
    - Multiple extraction methods for relations:
        * Pattern-based: Pattern matching for common relations
        * Regex-based: Advanced regex relation extraction
        * Co-occurrence: Proximity-based relation detection
        * Dependency: Dependency parsing-based extraction
        * HuggingFace: Custom HuggingFace relation models
        * LLM-based: LLM-powered relation extraction
    - Multiple extraction methods for triplets:
        * Pattern-based: Pattern matching for triplet extraction
        * Rules-based: Rule-based triplet extraction
        * HuggingFace: Custom HuggingFace triplet models
        * LLM-based: LLM-powered triplet extraction
    - Method dispatchers with registry support
    - Custom method registration capability
    - Consistent interface across all methods

Main Functions:
    - extract_entities_pattern: Pattern-based entity extraction
    - extract_entities_regex: Regex-based entity extraction
    - extract_entities_rules: Rule-based entity extraction
    - extract_entities_ml: ML-based (spaCy) entity extraction
    - extract_entities_huggingface: HuggingFace model entity extraction
    - extract_entities_llm: LLM-based entity extraction
    - extract_relations_pattern: Pattern-based relation extraction
    - extract_relations_regex: Regex-based relation extraction
    - extract_relations_cooccurrence: Co-occurrence relation extraction
    - extract_relations_dependency: Dependency parsing relation extraction
    - extract_relations_huggingface: HuggingFace relation extraction
    - extract_relations_llm: LLM-based relation extraction
    - extract_triplets_pattern: Pattern-based triplet extraction
    - extract_triplets_rules: Rule-based triplet extraction
    - extract_triplets_huggingface: HuggingFace triplet extraction
    - extract_triplets_llm: LLM-based triplet extraction
    - get_entity_method: Get entity extraction method by name
    - get_relation_method: Get relation extraction method by name
    - get_triplet_method: Get triplet extraction method by name

Example Usage:
    >>> from semantica.semantic_extract.methods import get_entity_method
    >>> extract_fn = get_entity_method("llm")
    >>> entities = extract_fn("Apple Inc. was founded in 1976.", provider="openai")

Author: Semantica Contributors
License: MIT
"""

import re
from typing import Any, Dict, List, Optional, Union

from ..utils.exceptions import ProcessingError
from ..utils.logging import get_logger
from .ner_extractor import Entity
from .providers import HuggingFaceModelLoader, create_provider
from .registry import method_registry
from .relation_extractor import Relation
from .triplet_extractor import Triplet

logger = get_logger("methods")

# Try to import spaCy
try:
    import spacy

    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


# ============================================================================
# Entity Extraction Methods
# ============================================================================


def extract_entities_pattern(text: str, **kwargs) -> List[Entity]:
    """Pattern-based entity extraction using regex."""
    entities = []

    patterns = {
        "PERSON": r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b",
        "ORG": r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\s+(?:Inc|Corp|LLC|Ltd|Company))\b",
        "GPE": r"\b([A-Z][a-z]+\s*(?:City|State|Country|Nation))\b",
        "DATE": r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4})\b",
    }

    for label, pattern in patterns.items():
        for match in re.finditer(pattern, text):
            entities.append(
                Entity(
                    text=match.group(1) if match.groups() else match.group(0),
                    label=label,
                    start_char=match.start(),
                    end_char=match.end(),
                    confidence=0.7,
                    metadata={"extraction_method": "pattern"},
                )
            )

    return entities


def extract_entities_regex(
    text: str, patterns: Optional[Dict[str, str]] = None, **kwargs
) -> List[Entity]:
    """Advanced regex-based entity extraction with custom patterns."""
    entities = []

    if patterns is None:
        patterns = {
            "PERSON": r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b",
            "ORG": r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\s+(?:Inc|Corp|LLC|Ltd|Company|Corporation))\b",
            "GPE": r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b",
            "DATE": r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4})\b",
            "MONEY": r"\b(\$[\d,]+(?:\.\d{2})?)\b",
            "PERCENT": r"\b(\d+(?:\.\d+)?%)\b",
        }

    for label, pattern in patterns.items():
        for match in re.finditer(pattern, text, re.IGNORECASE):
            entities.append(
                Entity(
                    text=match.group(1) if match.groups() else match.group(0),
                    label=label,
                    start_char=match.start(),
                    end_char=match.end(),
                    confidence=0.75,
                    metadata={"extraction_method": "regex", "pattern": pattern},
                )
            )

    return entities


def extract_entities_rules(text: str, **kwargs) -> List[Entity]:
    """Rule-based entity extraction using linguistic rules."""
    entities = []
    words = text.split()

    # Rule: Capitalized words at sentence start are likely entities
    sentences = re.split(r"[.!?]+", text)
    char_offset = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            char_offset += 1
            continue

        words_in_sent = sentence.split()
        if words_in_sent:
            first_word = words_in_sent[0]
            if first_word and first_word[0].isupper() and len(first_word) > 2:
                start = text.find(first_word, char_offset)
                if start >= 0:
                    entities.append(
                        Entity(
                            text=first_word,
                            label="PERSON",  # Default assumption
                            start_char=start,
                            end_char=start + len(first_word),
                            confidence=0.6,
                            metadata={
                                "extraction_method": "rules",
                                "rule": "sentence_start",
                            },
                        )
                    )

        char_offset += len(sentence) + 1

    return entities


def extract_entities_ml(
    text: str, model: str = "en_core_web_sm", **kwargs
) -> List[Entity]:
    """ML-based entity extraction using spaCy."""
    if not SPACY_AVAILABLE:
        logger.warning("spaCy not available, falling back to pattern extraction")
        return extract_entities_pattern(text, **kwargs)

    try:
        nlp = spacy.load(model)
    except OSError:
        logger.warning(f"spaCy model {model} not found, using en_core_web_sm")
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning(
                "spaCy model not available, falling back to pattern extraction"
            )
            return extract_entities_pattern(text, **kwargs)

    doc = nlp(text)
    entities = []

    for ent in doc.ents:
        confidence = 1.0
        if hasattr(ent, "confidence"):
            confidence = ent.confidence
        elif hasattr(ent, "score"):
            confidence = ent.score

        entities.append(
            Entity(
                text=ent.text,
                label=ent.label_,
                start_char=ent.start_char,
                end_char=ent.end_char,
                confidence=confidence,
                metadata={
                    "extraction_method": "ml",
                    "model": model,
                    "lemma": ent.lemma_ if hasattr(ent, "lemma_") else ent.text,
                },
            )
        )

    return entities


def extract_entities_huggingface(
    text: str,
    model: str = "dslim/bert-base-NER",
    device: Optional[str] = None,
    **kwargs,
) -> List[Entity]:
    """HuggingFace entity extraction."""
    loader = HuggingFaceModelLoader(device=device)
    model_obj = loader.load_ner_model(model)
    results = loader.extract_entities(model_obj, text)

    entities = []
    for result in results:
        if isinstance(result, dict):
            entities.append(
                Entity(
                    text=result.get("word", result.get("entity", "")),
                    label=result.get("entity_group", result.get("label", "UNKNOWN")),
                    start_char=result.get("start", 0),
                    end_char=result.get("end", 0),
                    confidence=result.get("score", 1.0),
                    metadata={"model": model, "extraction_method": "huggingface"},
                )
            )

    return entities


def extract_entities_llm(
    text: str, provider: str = "openai", model: Optional[str] = None, **kwargs
) -> List[Entity]:
    """LLM-based entity extraction."""
    # Support llm_model parameter to disambiguate from ML model
    if "llm_model" in kwargs:
        model = kwargs.pop("llm_model")

    llm = create_provider(provider, model=model, **kwargs)

    if not llm.is_available():
        raise ProcessingError(f"{provider} provider not available")

    # Use custom entity types if provided, otherwise use defaults
    entity_types = kwargs.get("entity_types")
    if entity_types:
        entity_types_str = ", ".join(entity_types)
        entity_types_instruction = f"""Preferred entity types: {entity_types_str}.
You may also use related or similar entity types if they better match the context (e.g., variations, synonyms, or domain-specific types).
If an entity doesn't fit any of the preferred types, use the most appropriate type from the preferred list or a closely related type."""
    else:
        entity_types_instruction = """Entity types should be one of: PERSON, ORG, GPE, DATE, EVENT, PRODUCT, CONCEPT, or related types.
Use the most appropriate type for each entity, including variations or synonyms if they better match the context."""

    prompt = f"""Extract named entities from the following text. 
Return ONLY a valid JSON list of objects with the following structure:
[
  {{"text": "entity name", "label": "ENTITY_TYPE", "start": 0, "end": 10, "confidence": 0.9}}
]

{entity_types_instruction}
Do not include any conversational filler, explanations, or markdown formatting outside the JSON block.

Text: {text}"""

    try:
        result = llm.generate_structured(prompt)
        entities = []

        if isinstance(result, list):
            for item in result:
                entities.append(
                    Entity(
                        text=item.get("text", ""),
                        label=item.get("label", "UNKNOWN"),
                        start_char=item.get("start", 0),
                        end_char=item.get("end", 0),
                        confidence=item.get("confidence", 0.9),
                        metadata={
                            "provider": provider,
                            "model": model,
                            "extraction_method": "llm",
                        },
                    )
                )
        elif isinstance(result, dict) and "entities" in result:
            for item in result["entities"]:
                entities.append(
                    Entity(
                        text=item.get("text", ""),
                        label=item.get("label", "UNKNOWN"),
                        start_char=item.get("start", 0),
                        end_char=item.get("end", 0),
                        confidence=item.get("confidence", 0.9),
                        metadata={
                            "provider": provider,
                            "model": model,
                            "extraction_method": "llm",
                        },
                    )
                )

        return entities
    except Exception as e:
        logger.error(f"LLM entity extraction failed: {e}")
        return []


# ============================================================================
# Relation Extraction Methods
# ============================================================================


def extract_relations_pattern(
    text: str, entities: List[Entity], **kwargs
) -> List[Relation]:
    """Pattern-based relation extraction."""
    relations = []

    if not entities:
        return []

    # Create entity pattern from provided entities
    # Sort by length descending to match longest entities first (e.g. "Apple Inc." before "Apple")
    sorted_entities = sorted(entities, key=lambda e: len(e.text), reverse=True)
    
    # Escape entity texts and join with OR
    # We use a non-capturing group for the alternatives
    entity_texts = [re.escape(e.text) for e in sorted_entities]
    # Remove duplicates
    entity_texts = list(dict.fromkeys(entity_texts))
    
    if not entity_texts:
        return []
        
    ent_pat = f"(?:{'|'.join(entity_texts)})"
    
    # Use entity pattern for subject as well, since we require the subject to be a known entity
    # This prevents matching long strings of text that happen to end with a relation keyword
    subject_pat = ent_pat

    relation_patterns = {
        "founded_by": [
            fr"(?P<subject>{subject_pat})\s+(?:was\s+)?founded\s+by\s+(?P<object>{ent_pat})",
            fr"(?P<object>{ent_pat})\s+founded\s+(?P<subject>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+(?:was\s+)?established\s+by\s+(?P<object>{ent_pat})",
            fr"(?P<object>{ent_pat})\s+established\s+(?P<subject>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+(?:was\s+)?created\s+by\s+(?P<object>{ent_pat})",
            fr"(?P<object>{ent_pat})\s+created\s+(?P<subject>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+(?:was\s+)?started\s+by\s+(?P<object>{ent_pat})",
            fr"(?P<object>{ent_pat})\s+started\s+(?P<subject>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+(?:was\s+)?co-founded\s+by\s+(?P<object>{ent_pat})",
            fr"(?P<object>{ent_pat})\s+co-founded\s+(?P<subject>{ent_pat})",
            fr"(?P<object>{ent_pat})\s+is\s+(?:the\s+)?founder\s+of\s+(?P<subject>{ent_pat})",
        ],
        "located_in": [
            fr"(?P<subject>{subject_pat})\s+is\s+located\s+in\s+(?P<object>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+in\s+(?P<object>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+(?:is\s+)?headquartered\s+in\s+(?P<object>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+(?:is\s+)?based\s+in\s+(?P<object>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+has\s+(?:its\s+)?headquarters\s+in\s+(?P<object>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+operates\s+(?:out\s+of|from)\s+(?P<object>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+has\s+offices\s+in\s+(?P<object>{ent_pat})",
        ],
        "works_for": [
            fr"(?P<subject>{subject_pat})\s+works?\s+for\s+(?P<object>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+works?\s+at\s+(?P<object>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+is\s+an?\s+employee\s+of\s+(?P<object>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+is\s+(?:the\s+)?(?:CEO|CFO|CTO|COO|director|manager|president|founder)\s+of\s+(?P<object>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+joined\s+(?P<object>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+was\s+hired\s+by\s+(?P<object>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+serves\s+at\s+(?P<object>{ent_pat})",
        ],
        "born_in": [
            fr"(?P<subject>{subject_pat})\s+was\s+born\s+in\s+(?P<object>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+born\s+in\s+(?P<object>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+is\s+a\s+native\s+of\s+(?P<object>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+hails\s+from\s+(?P<object>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+is\s+originally\s+from\s+(?P<object>{ent_pat})",
        ],
        "acquired_by": [
            fr"(?P<subject>{subject_pat})\s+(?:was\s+)?acquired\s+by\s+(?P<object>{ent_pat})",
            fr"(?P<object>{ent_pat})\s+acquired\s+(?P<subject>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+(?:was\s+)?bought\s+by\s+(?P<object>{ent_pat})",
            fr"(?P<object>{ent_pat})\s+bought\s+(?P<subject>{ent_pat})",
            fr"(?P<subject>{subject_pat})\s+is\s+a\s+subsidiary\s+of\s+(?P<object>{ent_pat})",
        ],
    }

    entity_map = {e.text.lower(): e for e in entities}
    # DEBUG: Print entities in map
    print(f"DEBUG: Entity map keys: {list(entity_map.keys())}")

    for relation_type, patterns in relation_patterns.items():
        for pattern in patterns:
            # DEBUG: Print pattern being tried
            # print(f"DEBUG: Trying pattern: {pattern}")
            for match in re.finditer(pattern, text, re.IGNORECASE):
                subject_text = match.group("subject").strip()
                object_text = match.group("object").strip()
                
                # DEBUG: Print match details
                print(f"DEBUG: Match found! Subject='{subject_text}', Object='{object_text}'")

                subject_entity = entity_map.get(subject_text.lower())
                object_entity = entity_map.get(object_text.lower())
                
                # DEBUG: Print lookup results
                print(f"DEBUG: Subject Entity found: {subject_entity is not None}, Object Entity found: {object_entity is not None}")

                if subject_entity and object_entity:
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end]

                    relations.append(
                        Relation(
                            subject=subject_entity,
                            predicate=relation_type,
                            object=object_entity,
                            confidence=0.7,
                            context=context,
                            metadata={
                                "extraction_method": "pattern",
                                "pattern": pattern,
                            },
                        )
                    )

    return relations


def extract_relations_regex(
    text: str,
    entities: List[Entity],
    patterns: Optional[Dict[str, List[str]]] = None,
    **kwargs,
) -> List[Relation]:
    """Advanced regex-based relation extraction."""
    if patterns is None:
        patterns = {
            "founded_by": [
                r"(?P<subject>\w+)\s+(?:was\s+)?founded\s+by\s+(?P<object>\w+(?:\s+\w+)*)"
            ],
            "located_in": [r"(?P<subject>\w+)\s+is\s+located\s+in\s+(?P<object>\w+)"],
        }

    relations = []
    entity_map = {e.text.lower(): e for e in entities}

    for relation_type, pattern_list in patterns.items():
        for pattern in pattern_list:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                subject_text = match.group("subject")
                object_text = match.group("object")

                subject_entity = entity_map.get(subject_text.lower())
                object_entity = entity_map.get(object_text.lower())

                if subject_entity and object_entity:
                    relations.append(
                        Relation(
                            subject=subject_entity,
                            predicate=relation_type,
                            object=object_entity,
                            confidence=0.75,
                            context=text[
                                max(0, match.start() - 30) : min(
                                    len(text), match.end() + 30
                                )
                            ],
                            metadata={"extraction_method": "regex"},
                        )
                    )

    return relations


def extract_relations_cooccurrence(
    text: str, entities: List[Entity], **kwargs
) -> List[Relation]:
    """Co-occurrence based relation extraction."""
    relations = []

    for i, entity1 in enumerate(entities):
        for entity2 in entities[i + 1 :]:
            distance = abs(entity1.end_char - entity2.start_char)
            if distance < 100:  # Within 100 characters
                start = min(entity1.start_char, entity2.start_char)
                end = max(entity1.end_char, entity2.end_char)
                context = text[max(0, start - 30) : min(len(text), end + 30)]

                relations.append(
                    Relation(
                        subject=entity1,
                        predicate="related_to",
                        object=entity2,
                        confidence=0.6,  # Meets default threshold
                        context=context,
                        metadata={
                            "extraction_method": "co_occurrence",
                            "distance": distance,
                        },
                    )
                )

    return relations


def extract_relations_dependency(
    text: str, entities: List[Entity], model: str = "en_core_web_sm", **kwargs
) -> List[Relation]:
    """Dependency parsing based relation extraction."""
    if not SPACY_AVAILABLE:
        logger.warning("spaCy not available, falling back to pattern extraction")
        return extract_relations_pattern(text, entities, **kwargs)

    try:
        nlp = spacy.load(model)
    except OSError:
        logger.warning(f"spaCy model {model} not found")
        return extract_relations_pattern(text, entities, **kwargs)

    doc = nlp(text)
    relations = []
    
    # Map tokens to entities
    token_to_entity = {}
    for token in doc:
        for entity in entities:
            # Check if token is within entity span
            if token.idx >= entity.start_char and (token.idx + len(token)) <= entity.end_char:
                token_to_entity[token] = entity
                break
    
    # DEBUG: Print token to entity mapping
    # print(f"DEBUG: Token to entity mapping keys: {[t.text for t in token_to_entity.keys()]}")

    # DEBUG: Dump full dependency tree
    # print("DEBUG: Dependency Tree:")
    # for token in doc:
    #     print(f"  {token.i}: {token.text} ({token.dep_}) -> {token.head.text} ({token.head.i})")

    # Helper to find entity for a token (or its head chain)
    def find_subject_entity(token):
        # 1. If acl, check head
        if token.dep_ == "acl":
            head = token.head
            if head in token_to_entity:
                return token_to_entity[head]
            
            # 2. If head is attr/acomp, check its head's nsubj
            if head.dep_ in ["attr", "acomp", "dobj"] and head.head.pos_ in ["VERB", "AUX"]:
                copula = head.head
                for child in copula.children:
                    if child.dep_ in ["nsubj", "nsubjpass"] and child in token_to_entity:
                        return token_to_entity[child]
        return None

    # Helper to expand objects via conjunctions
    def expand_conjunctions(token):
        results = [token]
        for child in token.children:
            if child.dep_ == "conj":
                results.extend(expand_conjunctions(child))
        return results

    for token in doc:
        # Check if token is a potential predicate (Verb)
        # We process verbs that have nsubj OR are acl OR are ROOT/VERB
        
        subject_entity = None
        
        # Case 1: Token has nsubj/nsubjpass
        nsubj = next((c for c in token.children if c.dep_ in ["nsubj", "nsubjpass"]), None)
        if nsubj:
            subject_entity = token_to_entity.get(nsubj)
        
        # Case 2: Token is acl or other modifier, try to infer subject from context
        if not subject_entity:
             subject_entity = find_subject_entity(token)
             
        if not subject_entity:
            continue

        verb = token
        # DEBUG: Print found subject
        # print(f"DEBUG: Found subject {subject_entity.text} for verb {verb.text}")

        # Find objects
        potential_objects = []
        for child in verb.children:
            # Direct objects
            if child.dep_ in ["dobj", "attr", "acomp"]:
                potential_objects.extend(expand_conjunctions(child))
                # Check for "attr of object" pattern (e.g. "CEO of Apple")
                for grandchild in child.children:
                    if grandchild.dep_ == "prep":
                        for greatgrandchild in grandchild.children:
                            if greatgrandchild.dep_ == "pobj":
                                potential_objects.extend(expand_conjunctions(greatgrandchild))
                                
            # Prepositional objects (including agent)
            elif child.dep_ in ["prep", "agent"]:
                for grandchild in child.children:
                    if grandchild.dep_ == "pobj":
                        potential_objects.extend(expand_conjunctions(grandchild))
        
        # DEBUG: Print potential objects
        # print(f"DEBUG: Potential objects for verb {verb.text}: {[t.text for t in potential_objects]}")

        for obj_token in potential_objects:
            object_entity = token_to_entity.get(obj_token)
            
            # DEBUG: Print object checking
            # print(f"DEBUG: Checking object token: {obj_token.text}, Entity: {object_entity}")

            if object_entity and subject_entity != object_entity:
                relations.append(
                    Relation(
                        subject=subject_entity,
                        predicate=verb.lemma_,
                        object=object_entity,
                        confidence=0.8,
                        context=text[
                            max(0, token.idx - 30) : min(
                                len(text), obj_token.idx + len(obj_token.text) + 30
                            )
                        ],
                        metadata={
                            "extraction_method": "dependency",
                            "dependency_path": f"{token.dep_} -> ... -> {obj_token.dep_}",
                        },
                    )
                )

    return relations


def extract_relations_huggingface(
    text: str,
    entities: List[Entity],
    model: str,
    device: Optional[str] = None,
    **kwargs,
) -> List[Relation]:
    """HuggingFace relation extraction."""
    loader = HuggingFaceModelLoader(device=device)
    model_obj = loader.load_relation_model(model)

    # This is simplified - actual implementation would depend on model architecture
    results = loader.extract_relations(model_obj, text, entities)

    relations = []
    # Parse results based on model output format
    # This is a placeholder - actual parsing would depend on the model
    return relations


def extract_relations_llm(
    text: str,
    entities: List[Entity],
    provider: str = "openai",
    model: Optional[str] = None,
    **kwargs,
) -> List[Relation]:
    """LLM-based relation extraction."""
    # Support llm_model parameter to disambiguate from ML model
    if "llm_model" in kwargs:
        model = kwargs.pop("llm_model")
    
    llm = create_provider(provider, model=model, **kwargs)

    if not llm.is_available():
        raise ProcessingError(f"{provider} provider not available")

    entities_str = ", ".join([f"{e.text} ({e.label})" for e in entities])
    
    # Use custom relation types if provided
    relation_types = kwargs.get("relation_types")
    if relation_types:
        relation_types_str = ", ".join(relation_types)
        relation_types_instruction = f"""
Preferred relation types: {relation_types_str}.
You may also use related or similar relation types if they better capture the relationship (e.g., variations, synonyms, or domain-specific relations).
If a relation doesn't fit any of the preferred types, use the most appropriate type from the preferred list or a closely related type that accurately describes the relationship."""
    else:
        relation_types_instruction = """
Extract meaningful relationships between entities. Use appropriate relation types that accurately describe how entities are connected.
Common relation types include: related_to, part_of, located_in, created_by, uses, depends_on, interacts_with, and similar variations."""
    
    prompt = f"""Extract relations between entities from the following text.

Text: {text}
Entities: {entities_str}{relation_types_instruction}

Return JSON format: [{{"subject": "...", "predicate": "...", "object": "...", "confidence": 0.9}}]
Extract all meaningful relationships between the entities, using the most appropriate relation type for each relationship."""

    try:
        result = llm.generate_structured(prompt)
        relations = []

        if isinstance(result, list):
            for item in result:
                # Find matching entities
                subject_text = item.get("subject", "")
                object_text = item.get("object", "")

                subject_entity = next(
                    (e for e in entities if e.text.lower() == subject_text.lower()),
                    None,
                )
                object_entity = next(
                    (e for e in entities if e.text.lower() == object_text.lower()), None
                )

                if subject_entity and object_entity:
                    relations.append(
                        Relation(
                            subject=subject_entity,
                            predicate=item.get("predicate", "related_to"),
                            object=object_entity,
                            confidence=item.get("confidence", 0.9),
                            context=text,
                            metadata={
                                "provider": provider,
                                "model": model,
                                "extraction_method": "llm",
                            },
                        )
                    )

        return relations
    except Exception as e:
        logger.error(f"LLM relation extraction failed: {e}")
        return []


# ============================================================================
# Triplet Extraction Methods
# ============================================================================


def extract_triplets_pattern(
    text: str,
    entities: Optional[List[Entity]] = None,
    relations: Optional[List[Relation]] = None,
    **kwargs,
) -> List[Triplet]:
    """Pattern-based triplet extraction."""
    triplets = []

    if relations:
        # Convert relations to triplets
        for relation in relations:
            triplets.append(
                Triplet(
                    subject=relation.subject.text,
                    predicate=relation.predicate,
                    object=relation.object.text,
                    confidence=relation.confidence,
                    metadata={"extraction_method": "pattern", **relation.metadata},
                )
            )
    elif entities:
        # Simple triplet extraction from entities
        # Look for subject-verb-object patterns
        pattern = r"(?P<subject>\w+)\s+(?P<predicate>\w+)\s+(?P<object>\w+)"
        for match in re.finditer(pattern, text):
            subject_text = match.group("subject")
            predicate_text = match.group("predicate")
            object_text = match.group("object")

            subject_entity = next(
                (e for e in entities if e.text.lower() == subject_text.lower()), None
            )
            object_entity = next(
                (e for e in entities if e.text.lower() == object_text.lower()), None
            )

            if subject_entity and object_entity:
                triplets.append(
                    Triplet(
                        subject=subject_entity.text,
                        predicate=predicate_text,
                        object=object_entity.text,
                        confidence=0.7,
                        metadata={"extraction_method": "pattern"},
                    )
                )

    return triplets


def extract_triplets_rules(
    text: str, entities: Optional[List[Entity]] = None, **kwargs
) -> List[Triplet]:
    """Rule-based triplet extraction."""
    triplets = []

    if not entities:
        return triplets

    # Rule: Look for verb patterns between entities
    sentences = re.split(r"[.!?]+", text)
    for sentence in sentences:
        words = sentence.split()
        for i, word in enumerate(words):
            if word.lower() in ["is", "was", "has", "founded", "located"]:
                # Look for entities before and after
                if i > 0 and i < len(words) - 1:
                    before = " ".join(words[:i])
                    after = " ".join(words[i + 1 :])

                    subject_entity = next(
                        (e for e in entities if e.text.lower() in before.lower()), None
                    )
                    object_entity = next(
                        (e for e in entities if e.text.lower() in after.lower()), None
                    )

                    if subject_entity and object_entity:
                        triplets.append(
                            Triplet(
                                subject=subject_entity.text,
                                predicate=word,
                                object=object_entity.text,
                                confidence=0.7,
                                metadata={"extraction_method": "rules"},
                            )
                        )

    return triplets


def extract_triplets_huggingface(
    text: str, model: str, device: Optional[str] = None, **kwargs
) -> List[Triplet]:
    """HuggingFace triplet extraction."""
    loader = HuggingFaceModelLoader(device=device)
    model_obj = loader.load_triplet_model(model)
    results = loader.extract_triplets(model_obj, text)

    triplets = []
    for result in results:
        # Parse result based on model output format
        # This is a placeholder - actual parsing would depend on the model
        if "triplet" in result:
            # Parse triplet string (format depends on model)
            pass

    return triplets


def extract_triplets_llm(
    text: str,
    entities: Optional[List[Entity]] = None,
    relations: Optional[List[Relation]] = None,
    provider: str = "openai",
    model: Optional[str] = None,
    **kwargs,
) -> List[Triplet]:
    """LLM-based triplet extraction."""
    llm = create_provider(provider, model=model, **kwargs)

    if not llm.is_available():
        raise ProcessingError(f"{provider} provider not available")

    prompt = f"""Extract RDF triplets (subject-predicate-object) from the following text.

Text: {text}

Return JSON format: [{{"subject": "...", "predicate": "...", "object": "...", "confidence": 0.9}}]"""

    try:
        result = llm.generate_structured(prompt)
        triplets = []

        if isinstance(result, list):
            for item in result:
                triplets.append(
                    Triplet(
                        subject=item.get("subject", ""),
                        predicate=item.get("predicate", ""),
                        object=item.get("object", ""),
                        confidence=item.get("confidence", 0.9),
                        metadata={
                            "provider": provider,
                            "model": model,
                            "extraction_method": "llm",
                        },
                    )
                )

        return triplets
    except Exception as e:
        logger.error(f"LLM triplet extraction failed: {e}")
        return []


# ============================================================================
# Method Dispatchers
# ============================================================================


def get_entity_method(method_name: str):
    """Get entity extraction method - checks registry for custom methods."""
    # Check registry first
    custom_method = method_registry.get("entity", method_name)
    if custom_method:
        return custom_method

    # Built-in methods
    builtin = {
        "pattern": extract_entities_pattern,
        "regex": extract_entities_regex,
        "rules": extract_entities_rules,
        "ml": extract_entities_ml,
        "spacy": extract_entities_ml,  # Alias for ml
        "huggingface": extract_entities_huggingface,
        "llm": extract_entities_llm,
    }

    method_func = builtin.get(method_name)
    if not method_func:
        raise ValueError(
            f"Unknown method: {method_name}. Register custom method or use built-in: {list(builtin.keys())}"
        )

    return method_func


def get_relation_method(method_name: str):
    """Get relation extraction method - checks registry for custom methods."""
    # Check registry first
    custom_method = method_registry.get("relation", method_name)
    if custom_method:
        return custom_method

    # Built-in methods
    builtin = {
        "pattern": extract_relations_pattern,
        "regex": extract_relations_regex,
        "cooccurrence": extract_relations_cooccurrence,
        "dependency": extract_relations_dependency,
        "ml": extract_relations_dependency,  # Alias for dependency
        "spacy": extract_relations_dependency,  # Alias for dependency
        "huggingface": extract_relations_huggingface,
        "llm": extract_relations_llm,
    }

    method_func = builtin.get(method_name)
    if not method_func:
        raise ValueError(
            f"Unknown method: {method_name}. Register custom method or use built-in: {list(builtin.keys())}"
        )

    return method_func


def get_triplet_method(method_name: str):
    """Get triplet extraction method - checks registry for custom methods."""
    # Check registry first
    custom_method = method_registry.get("triplet", method_name)
    if custom_method:
        return custom_method

    # Built-in methods
    builtin = {
        "pattern": extract_triplets_pattern,
        "rules": extract_triplets_rules,
        "huggingface": extract_triplets_huggingface,
        "llm": extract_triplets_llm,
    }

    method_func = builtin.get(method_name)
    if not method_func:
        raise ValueError(
            f"Unknown method: {method_name}. Register custom method or use built-in: {list(builtin.keys())}"
        )

    return method_func
