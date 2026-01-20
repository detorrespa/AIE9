"""
Distance metrics for vector similarity search.

This module provides multiple distance/similarity metrics that can be used
for comparing embeddings in the vector database.
"""

import numpy as np
from typing import Callable, Dict


def cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """
    Computes the cosine similarity between two vectors.
    
    Cosine similarity measures the cosine of the angle between two vectors.
    Range: [-1, 1] where 1 means identical direction, 0 means orthogonal, -1 means opposite.
    
    Args:
        vector_a: First vector
        vector_b: Second vector
    
    Returns:
        float: Cosine similarity score (higher is more similar)
    """
    dot_product = np.dot(vector_a, vector_b)
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)


def euclidean_distance(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """
    Computes the negative Euclidean distance between two vectors.
    
    Euclidean distance is the straight-line distance between two points.
    We return the negative value so that higher scores mean more similar
    (to maintain consistency with other metrics).
    
    Args:
        vector_a: First vector
        vector_b: Second vector
    
    Returns:
        float: Negative Euclidean distance (higher/less negative is more similar)
    """
    distance = np.linalg.norm(vector_a - vector_b)
    return -distance  # Negative so higher is better


def dot_product_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """
    Computes the dot product between two vectors.
    
    The dot product measures both the magnitude and direction similarity.
    For normalized vectors, this is equivalent to cosine similarity.
    
    Args:
        vector_a: First vector
        vector_b: Second vector
    
    Returns:
        float: Dot product (higher is more similar)
    """
    return np.dot(vector_a, vector_b)


def manhattan_distance(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """
    Computes the negative Manhattan (L1) distance between two vectors.
    
    Manhattan distance is the sum of absolute differences of coordinates.
    We return the negative value so that higher scores mean more similar.
    
    Args:
        vector_a: First vector
        vector_b: Second vector
    
    Returns:
        float: Negative Manhattan distance (higher/less negative is more similar)
    """
    distance = np.sum(np.abs(vector_a - vector_b))
    return -distance  # Negative so higher is better


# Dictionary of available metrics for easy access
AVAILABLE_METRICS: Dict[str, Callable[[np.ndarray, np.ndarray], float]] = {
    'cosine': cosine_similarity,
    'euclidean': euclidean_distance,
    'dot': dot_product_similarity,
    'manhattan': manhattan_distance,
}


def get_metric(metric_name: str) -> Callable[[np.ndarray, np.ndarray], float]:
    """
    Get a distance metric function by name.
    
    Args:
        metric_name: Name of the metric ('cosine', 'euclidean', 'dot', 'manhattan')
    
    Returns:
        Callable: The metric function
    
    Raises:
        ValueError: If metric_name is not recognized
    """
    if metric_name not in AVAILABLE_METRICS:
        raise ValueError(
            f"Unknown metric '{metric_name}'. "
            f"Available metrics: {list(AVAILABLE_METRICS.keys())}"
        )
    return AVAILABLE_METRICS[metric_name]


if __name__ == "__main__":
    # Demo of different metrics
    v1 = np.array([1, 2, 3])
    v2 = np.array([4, 5, 6])
    v3 = np.array([1, 2, 3])  # Same as v1
    
    print("Comparing v1 vs v2 (different vectors):")
    for name, metric in AVAILABLE_METRICS.items():
        score = metric(v1, v2)
        print(f"  {name:12s}: {score:.4f}")
    
    print("\nComparing v1 vs v3 (identical vectors):")
    for name, metric in AVAILABLE_METRICS.items():
        score = metric(v1, v3)
        print(f"  {name:12s}: {score:.4f}")
