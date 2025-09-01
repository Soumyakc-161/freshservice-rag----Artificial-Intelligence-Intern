# ingest.py
import json
import os
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# Model for local embeddings (small & fast). Change if you want another.
EMBED_MODEL = "all-MiniLM-L6-v2"

CHUNK_SIZE = 500
DATA_FILE = "data/docs.json"
EMBED_FILE = "data/embeddings.npy"
META_FILE = "data/metadata.json"

def chunk_text(text, max_length=CHUNK_SIZE):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

def build_index():
    print("Loading docs...")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        docs = json.load(f)

    text_chunks = []
    metas = []

    for idx, doc in enumerate(docs):
        content = doc.get("content", "")
        title = doc.get("title", "")
        url = doc.get("url", "")
        if not content:
            continue
        chunks = chunk_text(content)
        for cid, chunk in enumerate(chunks):
            text_chunks.append(chunk)
            metas.append({
                "doc_id": idx,
                "chunk_id": cid,
                "title": title,
                "url": url,
                "text_excerpt": chunk[:400]
            })

    print(f"Total chunks created: {len(text_chunks)}")
    print("Loading sentence-transformers model:", EMBED_MODEL)
    model = SentenceTransformer(EMBED_MODEL)

    # encode all chunks (this runs locally)
    print("Computing embeddings (locally)...")
    embeddings = model.encode(text_chunks, show_progress_bar=True, convert_to_numpy=True)

    os.makedirs("data", exist_ok=True)
    np.save(EMBED_FILE, embeddings)
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(metas, f, indent=2, ensure_ascii=False)

    print("✅ Saved embeddings and metadata.")
    return embeddings, metas

if __name__ == "__main__":
    build_index()
