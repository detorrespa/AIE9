"""
Enhanced Vector Database with metadata support and multiple distance metrics.
"""

import numpy as np
from collections import defaultdict
from typing import List, Tuple, Callable, Dict, Any, Optional
from aimakerspace.openai_utils.embedding import EmbeddingModel
from aimakerspace.distance_metrics import cosine_similarity, AVAILABLE_METRICS
import asyncio


class VectorDatabase:
    """
    Enhanced vector database that stores embeddings with metadata.
    
    Features:
    - Metadata support for categorization and filtering
    - Multiple distance metrics
    - Category-based filtering
    - Batch embedding generation
    """
    
    def __init__(self, embedding_model: EmbeddingModel = None):
        """
        Initialize the vector database.
        
        Args:
            embedding_model: Model to use for generating embeddings.
                           Defaults to EmbeddingModel() if not provided.
        """
        self.vectors = defaultdict(np.array)
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.embedding_model = embedding_model or EmbeddingModel()

    def insert(self, key: str, vector: np.array, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Insert a vector with optional metadata into the database.
        
        Args:
            key: The text/key associated with this vector
            vector: The embedding vector
            metadata: Optional metadata dict (e.g., {'category': 'Exercise', 'source': 'doc1.txt'})
        """
        self.vectors[key] = vector
        self.metadata[key] = metadata or {}

    def search(
        self,
        query_vector: np.array,
        k: int,
        distance_measure: Callable = cosine_similarity,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[str, float]]:
        """
        Search for the k most similar vectors.
        
        Args:
            query_vector: The query embedding vector
            k: Number of results to return
            distance_measure: Function to measure similarity/distance
            metadata_filter: Optional dict to filter results by metadata
                           e.g., {'category': 'Exercise'} to only return Exercise chunks
        
        Returns:
            List of (key, score) tuples, sorted by similarity (highest first)
        """
        # Filter by metadata if specified
        if metadata_filter:
            filtered_items = [
                (key, vector) 
                for key, vector in self.vectors.items()
                if self._matches_filter(key, metadata_filter)
            ]
        else:
            filtered_items = list(self.vectors.items())
        
        # Calculate scores
        scores = [
            (key, distance_measure(query_vector, vector))
            for key, vector in filtered_items
        ]
        
        # Sort by score (descending) and return top k
        return sorted(scores, key=lambda x: x[1], reverse=True)[:k]

    def _matches_filter(self, key: str, metadata_filter: Dict[str, Any]) -> bool:
        """
        Check if a document's metadata matches the filter criteria.
        
        Args:
            key: The document key
            metadata_filter: Dict of metadata key-value pairs to match
        
        Returns:
            True if all filter criteria match, False otherwise
        """
        doc_metadata = self.metadata.get(key, {})
        return all(
            doc_metadata.get(filter_key) == filter_value
            for filter_key, filter_value in metadata_filter.items()
        )

    def search_by_text(
        self,
        query_text: str,
        k: int,
        distance_measure: Callable = cosine_similarity,
        return_as_text: bool = False,
        category: Optional[str] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[str, float]]:
        """
        Search using a text query (automatically generates embedding).
        
        Args:
            query_text: The search query text
            k: Number of results to return
            distance_measure: Function to measure similarity
            return_as_text: If True, return only the text keys (no scores)
            category: Shorthand for filtering by category (same as metadata_filter={'category': category})
            metadata_filter: Optional dict to filter by metadata
        
        Returns:
            List of (text, score) tuples, or list of text if return_as_text=True
        """
        query_vector = self.embedding_model.get_embedding(query_text)
        
        # Build metadata filter
        if category and not metadata_filter:
            metadata_filter = {'category': category}
        elif category and metadata_filter:
            metadata_filter = {**metadata_filter, 'category': category}
        
        results = self.search(
            query_vector, 
            k, 
            distance_measure,
            metadata_filter=metadata_filter
        )
        
        return [result[0] for result in results] if return_as_text else results

    def retrieve_from_key(self, key: str) -> Optional[np.array]:
        """
        Retrieve a vector by its key.
        
        Args:
            key: The text/key to look up
        
        Returns:
            The vector if found, None otherwise
        """
        return self.vectors.get(key, None)
    
    def get_metadata(self, key: str) -> Dict[str, Any]:
        """
        Get metadata for a specific document.
        
        Args:
            key: The document key
        
        Returns:
            Metadata dict, or empty dict if not found
        """
        return self.metadata.get(key, {})

    async def abuild_from_list(
        self, 
        list_of_text: List[str],
        metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> "VectorDatabase":
        """
        Build the database from a list of texts (async).
        
        Args:
            list_of_text: List of text documents to embed
            metadata_list: Optional list of metadata dicts (same length as list_of_text)
        
        Returns:
            Self (for chaining)
        """
        embeddings = await self.embedding_model.async_get_embeddings(list_of_text)
        
        for i, (text, embedding) in enumerate(zip(list_of_text, embeddings)):
            metadata = metadata_list[i] if metadata_list and i < len(metadata_list) else {}
            self.insert(text, np.array(embedding), metadata)
        
        return self
    
    def get_categories(self) -> List[str]:
        """
        Get all unique categories in the database.
        
        Returns:
            List of unique category values
        """
        categories = set()
        for meta in self.metadata.values():
            if 'category' in meta:
                categories.add(meta['category'])
        return sorted(list(categories))
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the database.
        
        Returns:
            Dict with stats like total documents, categories, etc.
        """
        stats = {
            'total_documents': len(self.vectors),
            'categories': self.get_categories(),
            'category_counts': {}
        }
        
        # Count documents per category
        for meta in self.metadata.values():
            cat = meta.get('category', 'Unknown')
            stats['category_counts'][cat] = stats['category_counts'].get(cat, 0) + 1
        
        return stats


if __name__ == "__main__":
    # Demo usage
    list_of_text = [
        "I like to eat broccoli and bananas.",
        "I ate a banana and spinach smoothie for breakfast.",
        "Chinchillas and kittens are cute.",
        "My sister adopted a kitten yesterday.",
        "Look at this cute hamster munching on a piece of broccoli.",
    ]
    
    metadata_list = [
        {'category': 'Food', 'topic': 'vegetables'},
        {'category': 'Food', 'topic': 'breakfast'},
        {'category': 'Animals', 'topic': 'pets'},
        {'category': 'Animals', 'topic': 'cats'},
        {'category': 'Animals', 'topic': 'rodents'},
    ]

    vector_db = VectorDatabase()
    vector_db = asyncio.run(vector_db.abuild_from_list(list_of_text, metadata_list))
    
    print("Database stats:", vector_db.get_stats())
    
    # Search all
    print("\n--- Search: 'I think fruit is awesome!' (no filter) ---")
    results = vector_db.search_by_text("I think fruit is awesome!", k=2)
    for text, score in results:
        meta = vector_db.get_metadata(text)
        print(f"  [{meta.get('category')}] {score:.3f}: {text[:50]}")
    
    # Search with category filter
    print("\n--- Search: 'cute' (only Animals) ---")
    results = vector_db.search_by_text("cute", k=2, category='Animals')
    for text, score in results:
        meta = vector_db.get_metadata(text)
        print(f"  [{meta.get('category')}] {score:.3f}: {text[:50]}")
