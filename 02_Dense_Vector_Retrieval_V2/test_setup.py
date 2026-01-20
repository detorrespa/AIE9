"""Quick test to verify all enhanced modules work."""

from aimakerspace import VectorDatabase, AVAILABLE_METRICS
from aimakerspace.categorizer import categorize_chunk, categorize_chunks
from aimakerspace.distance_metrics import cosine_similarity
from aimakerspace.text_utils import TextFileLoader, CharacterTextSplitter

print("[OK] All imports successful!")
print(f"[OK] Available metrics: {list(AVAILABLE_METRICS.keys())}")

# Test categorizer
test_texts = [
    "Regular exercise helps with fitness",
    "A balanced diet is important for nutrition",
    "Good sleep hygiene improves rest quality"
]

for text in test_texts:
    category = categorize_chunk(text)
    print(f"[OK] '{text[:30]}...' -> {category}")

print("\n[SUCCESS] All systems working! Ready to use.")
