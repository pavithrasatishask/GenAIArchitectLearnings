from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI     
from langchain.chains import RetrievalQA
import os
from dotenv import load_dotenv

load_dotenv()

#Any document loaded
loader = TextLoader("earth.txt")
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
llm = ChatOpenAI(temperature=0)

#Creating the RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

def self_retriever(query):
    print("Query received:", query)
    first_ans = llm.predict(f"Quest: {query}\n Ans:")

    if "I don't know" in first_ans or "I am not sure" in first_ans or len(first_ans) < 20:
        print("Low Confidence, LLM is unsure, invoking retriever...")
        improved_ans = qa_chain.run(query)
        return improved_ans
    else:
        print("High Confidence, LLM is sure, returning answer...")
        return first_ans

response = self_retriever("what is the shape of the earth?")
print("Final Answer: ", response)


# if the output in not satisfactory, we can always re-run the retriever with a modified prompt or different parameters to get a better answer.
# llm.predict --> answer --> if not satisfied --> qa_chain.run(query) --> better answer
# qa_chain - retriever object + llm object