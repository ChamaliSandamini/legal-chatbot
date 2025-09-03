import os
import json

# --- 1. Load your law text ---
with open("data/law_text.txt", "r", encoding="utf-8") as f:
    full_text = f.read()

# --- 2. Chunking function ---
def chunk_text(text, max_length=1000, overlap=200):
    """
    Splits text into smaller overlapping chunks.
    max_length = number of words in each chunk
    overlap = how many words overlap between chunks
    """
    words = text.split()
    start = 0
    while start < len(words):
        end = min(start + max_length, len(words))
        chunk = " ".join(words[start:end])
        yield {"text": chunk, "start_word": start, "end_word": end}
        start += max_length - overlap

# --- 3. Save chunks safely to disk ---
output_file = "data/chunks.jsonl"
with open(output_file, "w", encoding="utf-8") as f:
    for chunk in chunk_text(full_text):
        f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

print(f"✅ Chunks written to {output_file}")
