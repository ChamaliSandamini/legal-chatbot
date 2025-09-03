import os
import json
import pickle
import faiss
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found in .env")

client = OpenAI(api_key=api_key)

# --- Load FAISS index ---
index = faiss.read_index("data/law_index.faiss")

# --- Load chunk texts for retrieval ---
with open("data/chunks_texts.json", "r", encoding="utf-8") as f:
    chunk_texts = json.load(f)

# --- Helper: embed a query ---
def embed_text(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(response.data[0].embedding, dtype="float32")

# --- Retrieve top-k relevant chunks ---
def retrieve_chunks(query, k=3):
    q_emb = embed_text(query).reshape(1, -1)
    distances, indices = index.search(q_emb, k)
    results = []
    for idx in indices[0]:
        results.append(chunk_texts[idx])
    return results

# # --- Generate answer using GPT ---
# def answer_question(query):
#     chunks = retrieve_chunks(query)
#     context = "\n\n".join(chunks)

#     prompt = f"""
# You are a legal assistant specialized in Ontario real estate law.
# Answer the user's question using only the information from the provided context.
# If the answer is not in the context, say "I could not find an answer in the law text."

# Context:
# {context}

# Question: {query}

# Answer in clear and simple language:
# """

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": prompt}],
#     )
#     return response.choices[0].message.content.strip()


def answer_question(query):
    chunks = retrieve_chunks(query)
    context = "\n\n".join(chunks)

    prompt = f"""
You are a legal assistant specialized in Ontario real estate law.

Answer the user's question using only the provided context.
Always include the **Act names, section numbers, and subsections** exactly as they appear in the context.
If the context does not contain such references, say: "No specific section or Act was found for this question."

Context:
{context}

Question: {query}

Answer clearly, with references:
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


# --- Main loop ---
print("🤖 Legal Chatbot ready! Type 'exit' to quit.")
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Chatbot: Goodbye!")
        break
    try:
        answer = answer_question(user_input)
        print("Chatbot:", answer)
    except Exception as e:
        print("Error:", e)
