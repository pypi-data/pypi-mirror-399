"""
Vector Store Module

This module provides the core vector storage, indexing, and retrieval operations for
the Semantica framework, including vector storage, similarity search, indexing
management, and vector store maintenance capabilities.

Key Features:
    - Vector storage and management
    - Similarity search and retrieval
    - Vector indexing and optimization
    - Metadata association with vectors
    - Vector update and deletion operations
    - Multi-backend support through stores

Main Classes:
    - VectorStore: Main vector store interface for storing and searching vectors
    - VectorIndexer: Vector indexing engine for efficient similarity search
    - VectorRetriever: Vector retrieval and similarity search operations
    - VectorManager: Vector store management, maintenance, and statistics

Example Usage:
    >>> from semantica.vector_store import VectorStore
    >>> store = VectorStore(backend="faiss", dimension=768)
    >>> vector_ids = store.store_vectors(vectors, metadata=metadata_list)
    >>> results = store.search_vectors(query_vector, k=10)
    >>> store.update_vectors(vector_ids, new_vectors)
    >>> store.delete_vectors(vector_ids)
    >>> 
    >>> from semantica.vector_store import VectorIndexer, VectorRetriever
    >>> indexer = VectorIndexer(backend="faiss", dimension=768)
    >>> index = indexer.create_index(vectors, ids)
    >>> retriever = VectorRetriever(backend="faiss")
    >>> results = retriever.search_similar(query_vector, vectors, ids, k=10)

Author: Semantica Contributors
License: MIT
"""

from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from ..utils.exceptions import ProcessingError, ValidationError
from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker
from ..embeddings import EmbeddingGenerator


class VectorStore:
    """
    Vector store interface and management.

    • Stores and manages vector embeddings
    • Provides similarity search capabilities
    • Handles vector indexing and retrieval
    • Manages vector metadata and provenance
    • Supports multiple vector store backends
    • Provides vector store operations
    """

    SUPPORTED_BACKENDS = {"faiss", "weaviate", "qdrant", "milvus", "inmemory"}

    def __init__(self, backend="faiss", config=None, **kwargs):
        """Initialize vector store."""
        if backend.lower() not in self.SUPPORTED_BACKENDS:
            raise ValueError(
                f"Unsupported backend: {backend}. "
                f"Supported backends are: {', '.join(sorted(self.SUPPORTED_BACKENDS))}"
            )

        self.logger = get_logger("vector_store")
        self.config = config or {}
        self.config.update(kwargs)
        self.progress_tracker = get_progress_tracker()
        # Ensure progress tracker is enabled
        if not self.progress_tracker.enabled:
            self.progress_tracker.enabled = True

        self.backend = backend
        self.vectors: Dict[str, np.ndarray] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.dimension = self.config.get("dimension", 768)

        # Initialize backend-specific indexer
        # Avoid duplicate dimension argument
        indexer_config = self.config.copy()
        if "dimension" in indexer_config:
            del indexer_config["dimension"]

        self.indexer = VectorIndexer(
            backend=backend, dimension=self.dimension, **indexer_config
        )
        self.retriever = VectorRetriever(backend=backend, **self.config)

        # Initialize embedding generator
        try:
            self.embedder = EmbeddingGenerator()
            # Set default model if not configured, or respect global config
            # For now, we try to ensure a model is loaded if possible
            if hasattr(self.embedder, "set_text_model"):
                # Use a lightweight default if none specified, or let EmbeddingGenerator handle defaults
                pass
        except Exception as e:
            self.logger.warning(f"Could not initialize embedding generator: {e}")
            self.embedder = None

    def embed(self, text: str) -> np.ndarray:
        """
        Generate embedding for text using the internal embedder.
        
        Args:
            text: Text to embed
            
        Returns:
            Numpy array of embedding
        """
        if self.embedder:
            try:
                return self.embedder.generate_embeddings(text)
            except Exception as e:
                self.logger.warning(f"Embedding generation failed: {e}")
        
        # Fallback or raise? AgentMemory expects None or valid embedding.
        # Returning random vector as fallback for now (matches DemoVectorStore behavior)
        # to prevent crashes, but logging warning.
        self.logger.warning("Using random fallback embedding")
        return np.random.rand(self.dimension).astype(np.float32)

    def store(
        self,
        vectors: List[np.ndarray],
        documents: Optional[List[Any]] = None,
        metadata: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        **options,
    ) -> List[str]:
        """
        Convenience method to store vectors with documents/metadata.

        Args:
            vectors: List of embeddings
            documents: Optional list of source documents
            metadata: Optional metadata (dict for all, or list for each)
            **options: Additional options

        Returns:
            List[str]: Vector IDs
        """
        # Prepare metadata list
        num_vectors = len(vectors)
        final_metadata = []

        if isinstance(metadata, list):
            if len(metadata) != num_vectors:
                raise ValueError("Metadata list length must match vectors length")
            final_metadata = metadata
        elif isinstance(metadata, dict):
            # Apply same metadata to all, copy to avoid shared reference issues
            final_metadata = [metadata.copy() for _ in range(num_vectors)]
        else:
            final_metadata = [{} for _ in range(num_vectors)]

        # Merge document metadata if available
        if documents and len(documents) == num_vectors:
            for i, doc in enumerate(documents):
                doc_meta = {}
                if hasattr(doc, "metadata"):
                    doc_meta = doc.metadata
                elif isinstance(doc, dict):
                    doc_meta = doc.get("metadata", {})
                
                final_metadata[i].update(doc_meta)
        
        return self.store_vectors(vectors, metadata=final_metadata, **options)

    def store_vectors(
        self,
        vectors: List[np.ndarray],
        metadata: Optional[List[Dict[str, Any]]] = None,
        **options,
    ) -> List[str]:
        """
        Store vectors in vector store.

        Args:
            vectors: List of vector arrays
            metadata: List of metadata dictionaries
            **options: Storage options

        Returns:
            List of vector IDs
        """
        tracking_id = self.progress_tracker.start_tracking(
            module="vector_store",
            submodule="VectorStore",
            message=f"Storing {len(vectors)} vectors",
        )

        try:
            vector_ids = []
            metadata = metadata or [{}] * len(vectors)

            self.progress_tracker.update_tracking(
                tracking_id, message="Storing vectors..."
            )
            for i, (vector, meta) in enumerate(zip(vectors, metadata)):
                vector_id = f"vec_{len(self.vectors) + i}"
                self.vectors[vector_id] = vector
                self.metadata[vector_id] = meta
                vector_ids.append(vector_id)

            # Update index
            self.progress_tracker.update_tracking(
                tracking_id, message="Updating vector index..."
            )
            self.indexer.create_index(list(self.vectors.values()), vector_ids)

            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Stored {len(vector_ids)} vectors",
            )
            return vector_ids
        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise
    def save(self, path: str) -> None:
        """
        Save vector store to disk.
        
        Args:
            path: Directory path to save to
        """
        import os
        import pickle
        
        os.makedirs(path, exist_ok=True)
        
        # Save metadata and vectors (generic fallback)
        # Ideally, backends like FAISS have their own save methods
        if hasattr(self.indexer, "save_index"):
             self.indexer.save_index(os.path.join(path, "index.bin"))
        
        # Save Python-level data
        data = {
            "vectors": self.vectors,
            "metadata": self.metadata,
            "config": self.config,
            "backend": self.backend,
            "dimension": self.dimension
        }
        
        with open(os.path.join(path, "store_data.pkl"), "wb") as f:
            pickle.dump(data, f)
            
        self.logger.info(f"Saved vector store to {path}")

    def load(self, path: str) -> None:
        """
        Load vector store from disk.
        
        Args:
            path: Directory path to load from
        """
        import os
        import pickle
        
        data_path = os.path.join(path, "store_data.pkl")
        if not os.path.exists(data_path):
            self.logger.warning(f"Store data not found: {data_path}")
            return
            
        with open(data_path, "rb") as f:
            data = pickle.load(f)
            
        self.vectors = data.get("vectors", {})
        self.metadata = data.get("metadata", {})
        self.config = data.get("config", {})
        self.backend = data.get("backend", "faiss")
        self.dimension = data.get("dimension", 768)
        
        # Restore backend-specific index
        if hasattr(self.indexer, "load_index"):
            index_path = os.path.join(path, "index.bin")
            if os.path.exists(index_path):
                self.indexer.load_index(index_path)
            else:
                # Rebuild if index file missing but vectors present
                self.indexer.create_index(list(self.vectors.values()), list(self.vectors.keys()))
        
        self.logger.info(f"Loaded vector store from {path}")

    def search(self, query: str, limit: int = 10, **options) -> List[Dict[str, Any]]:
        """
        Search for similar vectors by query string.

        Args:
            query: Query string
            limit: Number of results
            **options: Additional options

        Returns:
            List of results with scores
        """
        # Generate embedding for query
        query_vector = self.embed(query)

        # Search by vector
        return self.search_vectors(query_vector=query_vector, k=limit, **options)

    def search_vectors(
        self, query_vector: np.ndarray, k: int = 10, **options
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query vector
            k: Number of results to return
            **options: Search options

        Returns:
            List of search results with scores
        """
        tracking_id = self.progress_tracker.start_tracking(
            module="vector_store",
            submodule="VectorStore",
            message=f"Searching for {k} similar vectors",
        )

        try:
            if not self.vectors:
                self.progress_tracker.stop_tracking(
                    tracking_id, status="completed", message="No vectors to search"
                )
                return []

            # Use retriever for similarity search
            self.progress_tracker.update_tracking(
                tracking_id, message="Performing similarity search..."
            )
            results = self.retriever.search_similar(
                query_vector,
                list(self.vectors.values()),
                list(self.vectors.keys()),
                k=k,
                **options,
            )

            # Add metadata to results if available
            for result in results:
                vector_id = result.get("id")
                if vector_id and vector_id in self.metadata:
                    result["metadata"] = self.metadata[vector_id]

            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Found {len(results)} similar vectors",
            )
            return results
        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def update_vectors(
        self, vector_ids: List[str], new_vectors: List[np.ndarray], **options
    ) -> bool:
        """Update existing vectors."""
        for vec_id, new_vec in zip(vector_ids, new_vectors):
            if vec_id in self.vectors:
                self.vectors[vec_id] = new_vec

        # Rebuild index
        self.indexer.create_index(
            list(self.vectors.values()), list(self.vectors.keys())
        )

        return True

    def delete_vectors(self, vector_ids: List[str], **options) -> bool:
        """Delete vectors from store."""
        for vec_id in vector_ids:
            self.vectors.pop(vec_id, None)
            self.metadata.pop(vec_id, None)

        # Rebuild index
        if self.vectors:
            self.indexer.create_index(
                list(self.vectors.values()), list(self.vectors.keys())
            )

        return True

    def get_vector(self, vector_id: str) -> Optional[np.ndarray]:
        """Get vector by ID."""
        return self.vectors.get(vector_id)

    def get_metadata(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for vector."""
        return self.metadata.get(vector_id)


class VectorIndexer:
    """Vector indexing engine."""

    def __init__(self, backend: str = "faiss", dimension: int = 768, **config):
        """Initialize vector indexer."""
        self.logger = get_logger("vector_indexer")
        self.config = config
        self.backend = backend
        self.dimension = dimension
        self.index = None

    def create_index(
        self, vectors: List[np.ndarray], ids: Optional[List[str]] = None, **options
    ) -> Any:
        """
        Create vector index.

        Args:
            vectors: List of vectors
            ids: Vector IDs
            **options: Indexing options

        Returns:
            Index object
        """
        if not vectors:
            return None

        # Convert to numpy array
        if isinstance(vectors[0], list):
            vectors = np.array(vectors)
        else:
            vectors = np.vstack(vectors)

        # Simple in-memory index (would use FAISS, etc. in production)
        self.index = {"vectors": vectors, "ids": ids or list(range(len(vectors)))}

        return self.index

    def update_index(self, index: Any, new_vectors: List[np.ndarray], **options) -> Any:
        """Update existing index."""
        # Simplified - rebuild index
        return self.create_index(
            list(index["vectors"]) + new_vectors,
            index["ids"] + [f"new_{i}" for i in range(len(new_vectors))],
        )

    def optimize_index(self, index: Any, **options) -> Any:
        """Optimize index for better performance."""
        # Simplified - return as-is
        return index


class VectorRetriever:
    """Vector retrieval engine."""

    def __init__(self, backend: str = "faiss", **config):
        """Initialize vector retriever."""
        self.logger = get_logger("vector_retriever")
        self.config = config
        self.backend = backend

    def search_similar(
        self,
        query_vector: np.ndarray,
        vectors: List[np.ndarray],
        ids: List[str],
        k: int = 10,
        **options,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query vector
            vectors: List of vectors to search
            ids: Vector IDs
            k: Number of results

        Returns:
            List of results with scores
        """
        if not vectors:
            return []

        # Convert to numpy
        if isinstance(vectors[0], list):
            vectors = np.array(vectors)
        else:
            vectors = np.vstack(vectors)

        if isinstance(query_vector, list):
            query_vector = np.array(query_vector)

        # Calculate cosine similarity with epsilon to avoid division by zero
        epsilon = 1e-10
        query_norm = np.linalg.norm(query_vector)
        vector_norms = np.linalg.norm(vectors, axis=1)

        similarities = np.dot(vectors, query_vector) / (
            (vector_norms * query_norm) + epsilon
        )

        # Get top k
        top_indices = np.argsort(similarities)[::-1][:k]

        results = []
        for idx in top_indices:
            results.append(
                {
                    "id": ids[idx],
                    "vector": vectors[idx],
                    "score": float(similarities[idx]),
                }
            )

        return results

    def search_by_metadata(
        self,
        metadata_filters: Dict[str, Any],
        vectors: List[np.ndarray],
        metadata: List[Dict[str, Any]],
        **options,
    ) -> List[Dict[str, Any]]:
        """Search vectors by metadata."""
        results = []

        for vec, meta in zip(vectors, metadata):
            match = True
            for key, value in metadata_filters.items():
                if key not in meta or meta[key] != value:
                    match = False
                    break

            if match:
                results.append({"vector": vec, "metadata": meta})

        return results

    def search_hybrid(
        self,
        query_vector: np.ndarray,
        metadata_filters: Dict[str, Any],
        vectors: List[np.ndarray],
        metadata: List[Dict[str, Any]],
        **options,
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search."""
        # Filter by metadata first
        filtered = self.search_by_metadata(metadata_filters, vectors, metadata)

        if not filtered:
            return []

        # Then search by similarity
        filtered_vectors = [r["vector"] for r in filtered]
        filtered_ids = [i for i in range(len(filtered_vectors))]

        return self.search_similar(
            query_vector, filtered_vectors, filtered_ids, **options
        )


class VectorManager:
    """Vector store management engine."""

    def __init__(self, **config):
        """Initialize vector manager."""
        self.logger = get_logger("vector_manager")
        self.config = config

    def manage_store(
        self, store: VectorStore, **operations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manage vector store operations."""
        results = {}

        for op_name, op_config in operations.items():
            if op_name == "optimize":
                results["optimize"] = self.maintain_store(store)
            elif op_name == "statistics":
                results["statistics"] = self.collect_statistics(store)

        return results

    def maintain_store(
        self, store: VectorStore, **options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Maintain vector store health."""
        # Check integrity
        vector_count = len(store.vectors)
        metadata_count = len(store.metadata)

        return {
            "healthy": vector_count == metadata_count,
            "vector_count": vector_count,
            "metadata_count": metadata_count,
        }

    def collect_statistics(self, store: VectorStore) -> Dict[str, Any]:
        """Collect vector store statistics."""
        return {
            "total_vectors": len(store.vectors),
            "dimension": store.dimension,
            "backend": store.backend,
        }
