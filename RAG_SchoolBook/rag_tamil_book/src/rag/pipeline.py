# rag/pipeline.py
from rag.retriever import retrieve
from rag.answer_generator import generate_answer

def answer_question(question, top_k=5):
    contexts = retrieve(question, top_k=top_k)
    if not contexts:
        return {"answer": "No relevant context found.", "sources": []}
    ans = generate_answer(question, contexts, language="ta")
    sources = [f"{c['source']} (page {c['page']})" for c in contexts]
    return {"answer": ans, "sources": sources}
