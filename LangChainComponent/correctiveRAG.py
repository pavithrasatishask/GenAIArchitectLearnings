from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings  
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
import numpy as np

#Any document loaded or direct document information is given
docs = [Document(page_content="Large Language Models (LLMs) are advanced AI systems built on deep neural networks designed to process, understand and generate human-like text. By using massive datasets and billions of parameters, LLMs have transformed the way humans interact with technology. It learns patterns, grammar and context from text and can answer questions, write content, translate languages and many more. Mordern LLMs include ChatGPT (OpenAI), Google Gemini, Anthropic Claude, etc"),
        Document(page_content="A large language model (LLM) is a language model trained with self-supervised machine learning on a vast amount of text, designed for natural language processing tasks, especially language generation.[1][2] The largest and most capable LLMs are generative pre-trained transformers (GPTs) and provide the core capabilities of chatbots such as ChatGPT, Gemini and Claude. LLMs can be fine-tuned for specific tasks or guided by prompt engineering.[3] These models acquire predictive power regarding syntax, semantics, and ontologies[4] inherent in human language corpora, but they also inherit inaccuracies and biases present in the data they are trained on.[5]")]

#text splitter to split the loaded document into chunks
text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
chunks = text_splitter.split_documents(docs)

#Embedding model to convert text to vectors
embedding = OpenAIEmbeddings(openai_api_key="")

#Creating vector store from the text chunks and embeddings
vectorstore = FAISS.from_documents(chunks, embedding) 
#vectorstore = FAISS.from_documents(docs, embedding) 
vectorstore.save_local("faiss_index_correctiveRAG")

#retriever from the vector store, and define the LLM that will be used 
retriever = vectorstore.as_retriever()
llm = ChatOpenAI(model="gpt-4o-mini",openai_api_key="", temperature=0)

#Creating the RAG chain using LCEL (modern approach)
template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

qa_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def pick_best_answer(query, original, corrected):
    """Compare answers with context and pick the most grounded one."""
    
    # Get RAG context used for grounding
    retrieved_docs = retriever.invoke(query)
    context = " ".join([d.page_content for d in retrieved_docs])
    
    # Convert text → embeddings
    ctx_emb = embedding.embed_query(context)
    orig_emb = embedding.embed_query(original)
    corr_emb = embedding.embed_query(corrected)
    
    # Compare similarity
    sim_o = cosine_similarity(orig_emb, ctx_emb)
    sim_c = cosine_similarity(corr_emb, ctx_emb)
    
    print("\n--- Similarity Scores ---")
    print("LLM-only answer similarity:", sim_o)
    print("RAG answer similarity:", sim_c)
    
    return corrected if sim_c > sim_o else original


def corrective_retriever(query):
    print("Query received:", query)
    predictedAns = llm.invoke(f"Question: {query}\n Answer:").content
    correctedresponse = qa_chain.invoke(query)
    return predictedAns, correctedresponse

predictedAns, correctedresponse = corrective_retriever("Large language models?")
print(f"Original Answer: {predictedAns}\n Corrected Answer: {correctedresponse}")
final_answer = pick_best_answer("Large language models?", predictedAns, correctedresponse)
print("Final Answer: ", final_answer)

# generated 2 output - one from llm.predict & another from qa_chain.run
# Compare both the outputs and share the best one 
# llm.predict, qa_chain.run(query) --> better answer
# qa_chain - retriever object + llm object

#Difference between FAISS.from_texts & FAISS.from_documents

#from langchain_community.vectorstores import FAISS
#texts = ["hello world", "this is a test"]
#faiss_store = FAISS.from_texts(texts, embedding=embeddings)


#from langchain.schema import Document
#from langchain_community.vectorstores import FAISS
#docs = [
#    Document(page_content="hello world", metadata={"id": 1}),
#    Document(page_content="this is a test", metadata={"id": 2}),
#]
#faiss_store = FAISS.from_documents(docs, embedding=embedding)
