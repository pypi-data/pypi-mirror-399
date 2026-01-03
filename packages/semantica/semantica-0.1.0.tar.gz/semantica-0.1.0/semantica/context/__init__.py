"""
Context Engineering Module

This module provides comprehensive context engineering infrastructure for agents,
formalizing context as a graph of connections to enable meaningful agent
understanding and memory. It integrates RAG with knowledge graphs to provide
persistent context for intelligent agents.

Key Features:
    - High-level interface (AgentContext) for easy use
    - Context graph construction from entities, relationships, and conversations
    - Agent memory management with RAG integration
    - Entity linking across sources with URI assignment
    - Hybrid context retrieval (vector + graph + memory)
    - Conversation history management

Main Classes:
    - AgentContext: High-level interface for agent context management
    - ContextGraph: In-memory context graph store and builder methods
    - ContextNode: Context graph node data structure
    - ContextEdge: Context graph edge data structure
    - AgentMemory: Manages persistent agent memory with RAG
    - MemoryItem: Memory item data structure
    - EntityLinker: Links entities across sources with URIs
    - EntityLink: Entity link data structure
    - LinkedEntity: Linked entity with context
    - ContextRetriever: Retrieves relevant context from multiple sources
    - RetrievedContext: Retrieved context item data structure

Example Usage:
    >>> from semantica.context import AgentContext
    >>> context = AgentContext(vector_store=vs, knowledge_graph=kg)
    >>> memory_id = context.store("User asked about Python", conversation_id="conv1")
    >>> results = context.retrieve("Python programming")
    >>> stats = context.store(["Doc 1", "Doc 2"], extract_entities=True)
"""

from .agent_context import AgentContext
from .agent_memory import AgentMemory, MemoryItem
from .context_graph import ContextEdge, ContextGraph, ContextNode
from .context_retriever import ContextRetriever, RetrievedContext
from .entity_linker import EntityLink, EntityLinker, LinkedEntity

__all__ = [
    # High-level interface
    "AgentContext",
    # Main classes
    "ContextGraph",
    "ContextNode",
    "ContextEdge",
    "EntityLinker",
    "EntityLink",
    "LinkedEntity",
    "AgentMemory",
    "MemoryItem",
    "ContextRetriever",
    "RetrievedContext",
]

# Backward compatibility alias
ContextGraphBuilder = ContextGraph
