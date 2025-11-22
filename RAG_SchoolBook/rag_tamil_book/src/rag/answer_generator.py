# rag/answer_generator.py
import os
import openai
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")  # change if unavailable

def generate_answer(question, contexts, language="ta"):
    """
    contexts: list of dicts {"content","page","source"}
    returns answer text
    """
    # Build context string
    ctx_texts = []
    for c in contexts:
        excerpt = c["content"][:800].replace("\n", " ")
        ctx_texts.append(f"[page {c['page']}] {excerpt}")

    prompt = (
        f"You are a helpful assistant that answers questions using the 8th-standard Tamil book context.\n"
        f"Use the provided context below (do not hallucinate). Provide the final answer in Tamil and cite pages inline like [page N].\n\n"
        f"CONTEXT:\n{chr(10).join(ctx_texts)}\n\n"
        f"QUESTION: {question}\n\n"
        f"Answer concisely in Tamil and add citations to pages used."
    )

    # Use ChatCompletion API
    resp = openai.ChatCompletion.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.2,
    )
    return resp.choices[0].message["content"]
