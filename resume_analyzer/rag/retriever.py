import os
import glob
from rag.embeddings import get_embedding, cosine_similarity

KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")

_chunks: list[str] = []
_chunk_embeddings: list = []
_loaded = False


def _load_knowledge_base():
    
    global _loaded
    if _loaded:
        return

    for file_path in glob.glob(os.path.join(KNOWLEDGE_BASE_DIR, "*.txt")):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        paragraphs = [p.strip() for p in content.split("\n") if p.strip()]

        for paragraph in paragraphs:
            _chunks.append(paragraph)
            _chunk_embeddings.append(get_embedding(paragraph))

    _loaded = True


def retrieve(query: str, top_k: int = 4) -> list[str]:
    
    _load_knowledge_base()

    if not _chunks:
        return []

    query_embedding = get_embedding(query)
    scored = [
        (chunk, cosine_similarity(query_embedding, emb))
        for chunk, emb in zip(_chunks, _chunk_embeddings)
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)

    return [chunk for chunk, _score in scored[:top_k]]
