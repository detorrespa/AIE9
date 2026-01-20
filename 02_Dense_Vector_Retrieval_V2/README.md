# Enhanced RAG with Metadata Filtering

## 🚀 What's New in This Version?

This is an **enhanced version** of the Dense Vector Retrieval project with three major improvements:

### 1. ✅ **Metadata Support**
- Automatic categorization of documents (Exercise, Nutrition, Sleep, Stress, General)
- Filter search results by category
- Track source files and additional metadata
- Get statistics about your document collection

### 2. 📏 **Multiple Distance Metrics**
- **Cosine Similarity** (default) - Measures angle between vectors
- **Euclidean Distance** - Straight-line distance in vector space  
- **Dot Product** - Magnitude and direction similarity
- **Manhattan Distance** - Sum of absolute differences
- Easy comparison to find the best metric for your use case

### 3. 🏗️ **Better Code Structure**
- Organized folder structure (`aimakerspace/`, `notebooks/`, `data/`, `tests/`)
- Separate module for distance metrics
- Enhanced documentation
- Type hints and docstrings throughout

---

## 📁 Project Structure

```
03_Enhanced_RAG_MetadataFiltering/
├── aimakerspace/              # Core library
│   ├── __init__.py
│   ├── distance_metrics.py   # NEW: Multiple similarity metrics
│   ├── text_utils.py          # Document loading and splitting
│   ├── vectordatabase.py      # ENHANCED: Metadata support
│   └── openai_utils/          # OpenAI API wrappers
│       ├── chatmodel.py
│       ├── embedding.py
│       └── prompts.py
├── data/                      # Documents
│   ├── HealthWellnessGuide.txt
│   └── PMarcaBlogs.txt
├── notebooks/                 # Jupyter notebooks
│   └── Enhanced_RAG_Assignment.ipynb
├── images/                    # Diagrams and visualizations
├── tests/                     # Unit tests
├── pyproject.toml             # Dependencies
├── uv.lock                    # Lock file
└── README.md                  # This file
```

---

## 🛠️ Installation

1. **Install UV** (if you haven't already):
   ```bash
   # See https://docs.astral.sh/uv/
   ```

2. **Navigate to this directory**:
   ```bash
   cd 03_Enhanced_RAG_MetadataFiltering
   ```

3. **Sync dependencies**:
   ```bash
   uv sync -p 3.12
   ```

4. **Set up your OpenAI API key**:
   ```bash
   # Create a .env file
   echo "OPENAI_API_KEY=your-key-here" > .env
   ```

5. **Open the notebook**:
   ```bash
   uv run jupyter notebook notebooks/Enhanced_RAG_Assignment.ipynb
   ```

---

## 💡 Key Features Demonstrated

### Metadata Filtering

```python
from aimakerspace.vectordatabase import VectorDatabase

# Build database with automatic categorization
vector_db = VectorDatabase()
await vector_db.abuild_from_list(documents, metadata_list)

# Search only in Exercise documents
results = vector_db.search_by_text(
    "What exercises help with back pain?",
    k=3,
    category='Exercise'  # Filter by category
)

# Get database statistics
stats = vector_db.get_stats()
print(f"Total documents: {stats['total_documents']}")
print(f"Categories: {stats['categories']}")
```

### Multiple Distance Metrics

```python
from aimakerspace.distance_metrics import AVAILABLE_METRICS

# Compare different metrics
for metric_name in ['cosine', 'euclidean', 'dot', 'manhattan']:
    results = vector_db.search_by_text(
        query,
        k=3,
        distance_measure=AVAILABLE_METRICS[metric_name]
    )
    print(f"\n--- Using {metric_name} ---")
    for text, score in results:
        print(f"  {score:.3f}: {text[:50]}...")
```

### Auto-Categorization

```python
def categorize_chunk(text: str) -> str:
    """Automatically categorizes text into health topics"""
    text_lower = text.lower()
    
    if any(kw in text_lower for kw in ['exercise', 'workout', 'training']):
        return 'Exercise'
    elif any(kw in text_lower for kw in ['nutrition', 'food', 'diet']):
        return 'Nutrition'
    elif any(kw in text_lower for kw in ['sleep', 'rest', 'insomnia']):
        return 'Sleep'
    elif any(kw in text_lower for kw in ['stress', 'anxiety', 'meditation']):
        return 'Stress'
    else:
        return 'General'
```

---

## 📊 Comparison: Original vs Enhanced

| Feature | Original (02) | Enhanced (03) |
|---------|--------------|---------------|
| Distance Metrics | Cosine only | 4 metrics (cosine, euclidean, dot, manhattan) |
| Metadata Support | ❌ | ✅ Automatic categorization |
| Filtering | ❌ | ✅ By category, metadata |
| Code Structure | Flat | Organized (folders) |
| Statistics | ❌ | ✅ Document counts, categories |
| Auto-categorization | ❌ | ✅ By keywords |

---

## 🎯 Learning Outcomes

By completing this enhanced version, you'll learn:

1. **Metadata Management**: How to store and query additional information with vectors
2. **Distance Metrics**: Understanding different similarity measures and when to use them
3. **Filtering Techniques**: How to narrow search results based on criteria
4. **Code Organization**: Best practices for structuring ML projects
5. **Performance Comparison**: How to benchmark different approaches

---

## 📝 Assignment Tasks

1. ✅ Run the enhanced notebook
2. ✅ Experiment with different distance metrics - which works best for health queries?
3. ✅ Test category filtering - does it improve relevance?
4. ✅ Add your own categories or metadata fields
5. ✅ Create a simple comparison showing improvement over the original

---

## 🔍 Example Usage

```python
# Import enhanced components
from aimakerspace import VectorDatabase, AVAILABLE_METRICS
from aimakerspace.text_utils import TextFileLoader, CharacterTextSplitter

# Load and split documents
loader = TextFileLoader("data/HealthWellnessGuide.txt")
documents = loader.load_documents()
splitter = CharacterTextSplitter()
chunks = splitter.split_texts(documents)

# Auto-categorize each chunk
metadata_list = [
    {'category': categorize_chunk(chunk), 'source': 'HealthWellnessGuide.txt'}
    for chunk in chunks
]

# Build enhanced vector database
vector_db = VectorDatabase()
vector_db = await vector_db.abuild_from_list(chunks, metadata_list)

# Search with filtering
results = vector_db.search_by_text(
    "natural sleep remedies",
    k=3,
    category='Sleep',  # Only search sleep-related content
    distance_measure=AVAILABLE_METRICS['cosine']
)

# Display results with metadata
for text, score in results:
    meta = vector_db.get_metadata(text)
    print(f"[{meta['category']}] Score: {score:.3f}")
    print(f"  {text[:100]}...\n")
```

---

## 🎥 Video Walkthrough

When creating your Loom video, highlight:

1. **Before/After comparison**: Show the same query with and without filters
2. **Metric comparison**: Demonstrate different distance metrics on the same query
3. **Category statistics**: Show the distribution of documents across categories
4. **Improved relevance**: Examples where filtering improves results

---

## 🤝 Contributing

This is a learning project, but feel free to:
- Experiment with additional metrics
- Add new metadata fields
- Improve the categorization logic
- Share your findings!

---

## 📚 Resources

- [Original Assignment](../02_Dense_Vector_Retrieval/)
- [UV Documentation](https://docs.astral.sh/uv/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Vector Similarity Metrics](https://www.pinecone.io/learn/vector-similarity/)

---

## 🏆 Success Criteria

Your enhanced RAG is successful if:
- ✅ Category filtering returns more relevant results
- ✅ You can explain when to use different distance metrics
- ✅ The code is well-organized and documented
- ✅ You can demonstrate measurable improvements

---

**Built with ❤️ as part of the AI Makerspace Engineering Bootcamp**
