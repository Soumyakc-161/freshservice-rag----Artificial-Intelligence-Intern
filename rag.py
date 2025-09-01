import os
import json
import numpy as np
from sklearn.neighbors import NearestNeighbors
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Assign variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_PROJECT_ID = os.getenv("OPENAI_PROJECT_ID")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Debug print (safe)
print("Loaded API key (first 10 chars):", (OPENAI_API_KEY or "")[:10])
print("Loaded Project ID:", OPENAI_PROJECT_ID)
print("Loaded Model:", OPENAI_MODEL)

# File paths
EMBED_FILE = "data/embeddings.npy"
META_FILE = "data/metadata.json"

# Initialize OpenAI client
openai_client = None
if OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print("⚠️ Warning: Could not initialize OpenAI client:", e)
else:
    print("⚠️ Missing OpenAI API key in environment variables")

# Globals
embeddings = None
metas = None
nn = None


def load_index():
    """Load embeddings and metadata, build nearest neighbor index."""
    global embeddings, metas, nn
    if embeddings is None:
        embeddings = np.load(EMBED_FILE)
    if metas is None:
        with open(META_FILE, "r", encoding="utf-8") as f:
            metas = json.load(f)
    nn = NearestNeighbors(n_neighbors=8, metric="cosine")
    nn.fit(embeddings)
    return nn


def retrieve(query, top_k=4):
    """Retrieve top_k similar docs."""
    global nn, embeddings, metas
    if nn is None:
        nn = load_index()

    from sentence_transformers import SentenceTransformer
    st_model = SentenceTransformer("all-MiniLM-L6-v2")
    q_emb = st_model.encode([query], convert_to_numpy=True)

    distances, idxs = nn.kneighbors(q_emb.reshape(1, -1), n_neighbors=top_k)
    results = []
    for d, idx in zip(distances[0], idxs[0]):
        meta = metas[idx]
        similarity = 1.0 - float(d)  # cosine distance -> similarity
        results.append({"meta": meta, "similarity": similarity})
    return results


PROMPT_TEMPLATE = """
You are an assistant that extracts accurate information ONLY from Freshservice API documentation.

Task:
- Answer the user’s question using ONLY the provided documentation snippets.
- ALWAYS give the output in the following format:

---
curl command:
<the full working curl command here>

Explanation:
<step by step explanation of each parameter, header, and endpoint>

Sources:
- Title: <doc title>, URL: <doc url>
- Title: <doc title>, URL: <doc url>

Confidence: <float between 0 and 1>
---

Documentation snippets:
{snippets}

User Question:
{question}
"""


def answer_query(question, top_k=4):
    snippets = []
    results = retrieve(question, top_k=top_k)
    for r in results:
        m = r["meta"]
        snippets.append(
            f"---\nTitle: {m.get('title','')}\nURL: {m.get('url','')}\nExcerpt: {m.get('text_excerpt','')}\nSimilarity: {r['similarity']:.4f}"
        )
    context = "\n\n".join(snippets)
    prompt = PROMPT_TEMPLATE.format(snippets=context, question=question)

    if openai_client:
        resp = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict assistant that answers only from the provided docs and must follow the response format.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.0,
        )
        content = resp.choices[0].message.content.strip()
    else:
        content = "⚠️ OpenAI API key not found. Here are the retrieved snippets:\n\n" + context

    avg_sim = sum([r["similarity"] for r in results]) / max(1, len(results))
    citations = [
        {
            "title": r["meta"].get("title", ""),
            "url": r["meta"].get("url", ""),
            "similarity": r["similarity"],
        }
        for r in results
    ]
    return {"answer": content, "citations": citations, "confidence": float(avg_sim)}


if __name__ == "__main__":
    q = "Give me the curl command to create a ticket."
    result = answer_query(q)
    print("\n=== ANSWER ===\n", result["answer"])
    print("\n=== CONFIDENCE ===\n", result["confidence"])
    print("\n=== CITATIONS ===\n", result["citations"])
