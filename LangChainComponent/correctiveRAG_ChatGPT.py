import os
import numpy as np
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from rich.console import Console

console = Console()
# ---------------------------------------------------------
# LOAD SYSTEM PROMPT FROM EXTERNAL FILE
# ---------------------------------------------------------
def load_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

system_prompt = load_prompt("prompts/corrective_rag_system_prompt.txt")

def setup_environment():
    """Load and validate environment variables."""
    load_dotenv()

    required_vars = [
        "OPENAI_API_KEY",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        console.print(f"[bold red]Error: Missing required environment variables:[/bold red]")
        for var in missing_vars:
            console.print(f"  - {var}")
        console.print("\n[yellow]Please create a .env file based on .env.example[/yellow]")
        return False

    return True

# ---------------------------------------------------------
# SAMPLE DOCUMENTS
# In your product, replace with FAQ docs.
# ---------------------------------------------------------
docs = [
    Document(page_content="Large Language Models (LLMs) are advanced AI systems built on deep neural networks designed to process, understand and generate human-like text."),
    Document(page_content="Modern LLMs include ChatGPT (OpenAI), Google Gemini, Anthropic Claude, etc. They learn grammar, patterns, and contextual understanding from billions of parameters.")
]

# ---------------------------------------------------------
# TEXT SPLITTING
# ---------------------------------------------------------
text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=50)
chunks = text_splitter.split_documents(docs)

# ---------------------------------------------------------
# EMBEDDINGS + VECTOR STORE
# ---------------------------------------------------------
openai_api_key_value = os.getenv("OPENAI_API_KEY")
embedding = OpenAIEmbeddings(openai_api_key=openai_api_key_value)

vectorstore = FAISS.from_documents(chunks, embedding)
vectorstore.save_local("faiss_index_corrective_rag")

retriever = vectorstore.as_retriever()

# ---------------------------------------------------------
# LLM
# ---------------------------------------------------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    openai_api_key=openai_api_key_value
)

# ---------------------------------------------------------
# FORMAT DOCUMENTS
# ---------------------------------------------------------
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# ---------------------------------------------------------
# Corrective RAG Prompt Template
# ---------------------------------------------------------
prompt = ChatPromptTemplate.from_template(system_prompt)

# ---------------------------------------------------------
# BUILD THE Corrective RAG CHAIN USING LCEL
# ---------------------------------------------------------
corrective_rag_chain = (
    {
        "user_query": RunnablePassthrough(),
        "retrieved_context": retriever | format_docs
    }
    | prompt
    | llm
    | StrOutputParser()
)


# ---------------------------------------------------------
# UTILITY: COSINE SIMILARITY TO PICK BEST ANSWER
# ---------------------------------------------------------
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def pick_best_answer(query, original_answer, corrective_answer):
    """Compare semantic similarity to RAG context to choose the better answer."""
    retrieved_docs = retriever.invoke(query)
    context = " ".join([d.page_content for d in retrieved_docs])

    ctx_emb = embedding.embed_query(context)
    orig_emb = embedding.embed_query(original_answer)
    corr_emb = embedding.embed_query(corrective_answer)

    sim_original = cosine_similarity(orig_emb, ctx_emb)
    sim_corrective = cosine_similarity(corr_emb, ctx_emb)

    print(f"\nSimilarity Original LLM-only Answer: {sim_original}")
    print(f"Similarity Corrective RAG Answer: {sim_corrective}")

    return corrective_answer if sim_corrective > sim_original else original_answer


# ---------------------------------------------------------
# RUN Corrective RAG
# ---------------------------------------------------------
def answer_query(query: str):
    print("\n🔍 USER QUERY:", query)

    # LLM-only prediction (no RAG)
    original_answer = llm.invoke(f"Question: {query}\nAnswer:").content

    # Corrective RAG execution
    corrective_answer = corrective_rag_chain.invoke(query)

    print("\n--- RAW Outputs ---")
    print("LLM Only:", original_answer)
    print("Corrective RAG:", corrective_answer)

    # Pick the final answer based on similarity score
    final_answer = pick_best_answer(query, original_answer, corrective_answer)

    print("\n✅ FINAL SELECTED ANSWER:")
    print(final_answer)

    return final_answer


# ---------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------
if __name__ == "__main__":
    answer_query("What are large language models?")
