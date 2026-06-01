from groq import Groq

from app.core.config import settings
from app.services.embedder import embed_texts
from app.services.vector_store import search_chunks

client = Groq(api_key=settings.GROQ_API_KEY)


def answer_question(question: str, top_k: int = 5) -> dict:

    # Step 1: Embed the question
    question_vector = embed_texts([question])[0]

    # Step 2: Search Qdrant for relevant chunks
    chunks = search_chunks(query_vector=question_vector, top_k=top_k)

    if not chunks:
        return {
            "answer": "I could not find any relevant information in your documents.",
            "sources": [],
        }

    # Step 3: Build context from retrieved chunks
    context = ""
    for i, chunk in enumerate(chunks, start=1):
        context += f"[{i}] From '{chunk['filename']}' page {chunk['page']}:\n{chunk['text']}\n\n"

    # Step 4: Build the prompt
    prompt = f"""You are a helpful study assistant. Answer the question using ONLY the context provided below.
If the answer is not in the context, say "I don't have enough information in my documents to answer this."
At the end of your answer, mention which sources you used.

Context:
{context}

Question: {question}

Answer:"""

    # Step 5: Call Groq LLM
    response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    answer = response.choices[0].message.content

    # Step 6: Return answer + sources
    sources = [
        {
            "filename": chunk["filename"],
            "page": chunk["page"],
            "score": round(chunk["score"], 3),
        }
        for chunk in chunks
    ]

    return {
        "answer": answer,
        "sources": sources,
    }