from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings  
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

#Any text loaded
text = TextLoader("ragfromgeekofgeeks.txt").load()
textContent = text.load();

#Any pdf loaded
pdf = PyPDFLoader("LLM-Engineers-Handbook.pdf")
pdfcontent = pdf.load()

doc = [Document(page_content= textContent),Document(page_content= pdfcontent)]

#text splitter to split the loaded document into chunks
text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
chunks = text_splitter.split_documents(doc)

#Embedding model to convert text to vectors
embedding = OpenAIEmbeddings(openai_api_key="")

#Creating vector store from the text chunks and embeddings
vectorstore = FAISS.from_texts(documents=chunks, embedding=embedding)
vectorstore.save_local("faiss_index_fusionrag")

#retriever from the vector store, and define the LLM that will be used 
retriever = vectorstore.as_retriever()
llm = ChatOpenAI(temperature=0)

#Creating the RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=False)

def fusion_retriever(query):
    response = qa_chain.run(query)

response = fusion_retriever("What is Vector?")
print("Final Answer: ", response)


# if the output in not satisfactory, we can always re-run the retriever with a modified prompt or different parameters to get a better answer.
# llm.predict --> answer --> if not satisfied --> qa_chain.run(query) --> better answer
# qa_chain - retriever object + llm object