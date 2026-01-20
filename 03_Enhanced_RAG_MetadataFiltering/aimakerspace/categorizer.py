"""
Automatic categorization module for health and wellness documents.
"""

from typing import List, Dict


def categorize_chunk(text: str) -> str:
    """
    Automatically categorizes a text chunk into health/wellness topics.
    
    Args:
        text: The text chunk to categorize
    
    Returns:
        str: Category name ('Exercise', 'Nutrition', 'Sleep', 'Stress', or 'General')
    """
    text_lower = text.lower()
    
    # Define keywords for each category
    exercise_keywords = [
        'exercise', 'workout', 'training', 'physical', 'fitness',
        'stretch', 'muscle', 'cardio', 'strength', 'movement',
        'yoga', 'running', 'walking', 'gym', 'athletic'
    ]
    
    nutrition_keywords = [
        'nutrition', 'food', 'diet', 'eating', 'meal',
        'vitamin', 'protein', 'carb', 'fat', 'calorie',
        'vegetable', 'fruit', 'hydration', 'water', 'nutrient'
    ]
    
    sleep_keywords = [
        'sleep', 'rest', 'insomnia', 'bedtime', 'dream',
        'nap', 'fatigue', 'drowsy', 'circadian', 'rem',
        'mattress', 'pillow', 'bedroom', 'night'
    ]
    
    stress_keywords = [
        'stress', 'anxiety', 'meditation', 'mindfulness', 'relaxation',
        'mental', 'worry', 'calm', 'breathe', 'tension',
        'overwhelm', 'cope', 'pressure', 'zen', 'peace'
    ]
    
    # Count matches for each category
    category_scores = {
        'Exercise': sum(1 for kw in exercise_keywords if kw in text_lower),
        'Nutrition': sum(1 for kw in nutrition_keywords if kw in text_lower),
        'Sleep': sum(1 for kw in sleep_keywords if kw in text_lower),
        'Stress': sum(1 for kw in stress_keywords if kw in text_lower),
    }
    
    # Return category with highest score, or 'General' if no matches
    max_score = max(category_scores.values())
    if max_score == 0:
        return 'General'
    
    return max(category_scores.items(), key=lambda x: x[1])[0]


def categorize_chunks(chunks: List[str]) -> List[Dict[str, str]]:
    """
    Categorize a list of text chunks.
    
    Args:
        chunks: List of text chunks
    
    Returns:
        List of metadata dicts with 'category' field
    """
    return [{'category': categorize_chunk(chunk)} for chunk in chunks]


def get_category_distribution(metadata_list: List[Dict[str, str]]) -> Dict[str, int]:
    """
    Get the distribution of categories in a metadata list.
    
    Args:
        metadata_list: List of metadata dicts
    
    Returns:
        Dict mapping category names to counts
    """
    distribution = {}
    for meta in metadata_list:
        category = meta.get('category', 'Unknown')
        distribution[category] = distribution.get(category, 0) + 1
    return distribution


if __name__ == "__main__":
    # Demo
    test_texts = [
        "Regular exercise can help reduce lower back pain. Try stretching daily.",
        "A balanced diet rich in fruits and vegetables provides essential nutrients.",
        "Good sleep hygiene includes maintaining a consistent bedtime routine.",
        "Meditation and deep breathing can help manage stress and anxiety.",
        "This is just some random text without specific health topics."
    ]
    
    print("Categorization Demo:\n")
    for text in test_texts:
        category = categorize_chunk(text)
        print(f"[{category:12s}] {text}")
    
    metadata = categorize_chunks(test_texts)
    print("\nDistribution:", get_category_distribution(metadata))
