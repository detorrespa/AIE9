"""
Script to ingest matching_profiles.json into Qdrant.
Run AFTER existing ingest.py — adds profiles to the existing collection.

Usage: python scripts/ingest_matching_profiles.py
"""

import json
import uuid
from pathlib import Path

from langchain_ollama import OllamaEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from aria.config import settings

# ── Config ────────────────────────────────────────────────────────────────────
COLLECTION_NAME  = settings.qdrant_collection  # aria_documents
EMBED_MODEL      = settings.ollama_embed_model
PROFILES_PATH    = Path("documents/matching_profiles.json")

# ── Load profiles ─────────────────────────────────────────────────────────────
profiles = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
print(f"Loaded {len(profiles)} provider profiles")

# ── Embed + upsert ────────────────────────────────────────────────────────────
embeddings = OllamaEmbeddings(
    model=EMBED_MODEL,
    base_url=settings.ollama_base_url,
)
client = QdrantClient(path="./qdrant_data")

points = []
for p in profiles:
    text   = p["profile_text"]
    vector = embeddings.embed_query(text)
    points.append(PointStruct(
        id      = str(uuid.uuid4()),
        vector  = vector,
        payload = {
            "page_content": text,
            "metadata": {
                "source_name": p["source_name"],
                "provider":    p["provider"],
                "category":    p["category"],
                "domain":      p["domain"],
                "page_num":    0,
            }
        }
    ))

client.upsert(collection_name=COLLECTION_NAME, points=points)
print(f"Upserted {len(points)} provider profiles into '{COLLECTION_NAME}'")

# ── Verify ────────────────────────────────────────────────────────────────────
from qdrant_client.models import Filter, FieldCondition, MatchValue
result = client.count(
    collection_name = COLLECTION_NAME,
    count_filter    = Filter(must=[
        FieldCondition(key="metadata.category", match=MatchValue(value="matching"))
    ])
)
print(f"Total matching-category chunks after upsert: {result.count}")
