import os
import json
import faiss
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import time

# --- Load API key ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key not found. Make sure .env is set correctly.")
client = OpenAI(api_key=api_key)

# --- Load chunks ---
chunks_file = "data/chunks.jsonl"
chunks = []
with open(chunks_file, "r", encoding="utf-8") as f:
    for line in f:
        chunks.append(json.loads(line))

print(f"Loaded {len(chunks)} chunks")
if len(chunks) == 0:
    raise ValueError("No chunks found. Run chunk_and_prepare.py first.")

texts = [c["text"] for c in chunks]

# --- Generate embeddings ---
embeddings = []
for i, text in enumerate(texts):
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        emb = response.data[0].embedding
        embeddings.append(emb)
    except Exception as e:
        print(f"Error generating embedding for chunk {i}: {e}")
        embeddings.append([0.0]*1536)  # fallback vector
    if (i+1) % 10 == 0 or i+1 == len(texts):
        print(f"Embedded {i+1}/{len(texts)} chunks")
        time.sleep(0.2)  # gentle pause

# --- Convert to numpy array ---
embeddings = np.array(embeddings, dtype="float32")
if embeddings.ndim == 1:
    embeddings = embeddings.reshape(1, -1)
print("Embeddings shape:", embeddings.shape)

# --- Build FAISS index ---
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
faiss.write_index(index, "data/law_index.faiss")
print("✅ FAISS index saved to data/law_index.faiss")

# --- Save texts for lookup ---
with open("data/chunks_texts.json", "w", encoding="utf-8") as f:
    json.dump(texts, f, ensure_ascii=False, indent=2)
print("✅ Chunks texts saved to data/chunks_texts.json")
