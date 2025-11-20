from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

#Any document loaded
import os
# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
earth_file = os.path.join(script_dir, "earth.txt")
loader = TextLoader(earth_file)
loaded_text = loader.load()

#text splitter to split the loaded document into chunks
text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
chunks = text_splitter.split_documents(loaded_text)

#Embedding model to convert text to vectors
embedding = OpenAIEmbeddings(openai_api_key="")

#Creating vector store from the text chunks and embeddings
vectorstore = FAISS.from_documents(documents=chunks, embedding=embedding)
vectorstore.save_local("faiss_index_selfrag")

#retriever from the vector store, and define the LLM that will be used 
retriever = vectorstore.as_retriever()
llm = ChatOpenAI(temperature=0, openai_api_key="openai_api_key=openai_api_key=")

#Creating the RAG chain using LCEL (LangChain Expression Language - modern approach)
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

def self_retriever(query):
    print("Query received:", query)
    # Get LLM's initial answer without context
    first_ans = llm.invoke(f"Question: {query}\nAnswer:").content

    if "I don't know" in first_ans or "I am not sure" in first_ans or "I'm sorry" or len(first_ans) < 20:
        print("Low Confidence, LLM is unsure, invoking retriever...")
        improved_ans = qa_chain.invoke(query)
        return improved_ans
    else:
        print("High Confidence, LLM is sure, returning answer...")
        return first_ans

response = self_retriever("do you know who i am ?")
print("Final Answer: ", response)


# if the output in not satisfactory, we can always re-run the retriever with a modified prompt or different parameters to get a better answer.
# llm.predict --> answer --> if not satisfied --> qa_chain.run(query) --> better answer
# qa_chain - retriever object + llm object