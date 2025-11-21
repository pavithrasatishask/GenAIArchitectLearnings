import streamlit as st
from PyPDF2 import PdfReader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings  
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

st.title("RAG Chatbot: Ask Questions From Your PDF")

uploaded_file = st.file_uploader("Upload your PDF file", type=["pdf"])

if uploaded_file is not None:

    # STEP 1: READ PDF
    raw_text = ""
    try:
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                raw_text += text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")

    if not raw_text.strip():
        st.error("No text extracted from the PDF. Try another file.")
    else:
        # STEP 2: SPLIT TEXT
        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_text(raw_text)

        st.success(f"PDF loaded successfully! Created {len(chunks)} chunks.")

        # STEP 3: CREATE VECTORSTORE
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_texts(
            chunks, 
            embeddings,
            metadatas=[{"source": str(i)} for i in range(len(chunks))]
        )

        retriever = vectorstore.as_retriever()

        # STEP 4: BUILD LCEL RAG CHAIN
        template = """
        Answer the question based ONLY on the following context:

        {context}

        Question: {question}
        """

        prompt = ChatPromptTemplate.from_template(template)

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=openai_api_key
        )

        rag_chain = (
            {
                "context": retriever,
                "question": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        # STEP 5: USER QUESTION
        user_question = st.text_input("Ask a question about the PDF:")

        if user_question:
            with st.spinner("Searching & generating answer…"):
                answer = rag_chain.invoke(user_question)

            st.subheader("Answer")
            st.write(answer)
