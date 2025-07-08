# CSV and PDF uploader to parse & inject into RAG + KG
import streamlit as st
from langchain_community.document_loaders import CSVLoader, PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import CharacterTextSplitter

def handle_upload():
    uploaded_file = st.file_uploader("Upload CSV or PDF", type=["csv", "pdf"])
    
    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            with open("uploaded.csv", "wb") as f:
                f.write(uploaded_file.read())
            loader = CSVLoader(file_path="uploaded.csv")
        else:
            with open("uploaded.pdf", "wb") as f:
                f.write(uploaded_file.read())
            loader = PyMuPDFLoader("uploaded.pdf")
        
        docs = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_docs = text_splitter.split_documents(docs)

        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        db = FAISS.from_documents(split_docs, embeddings)
        db.save_local("custom_isro_vectorstore")

        st.success("✅ File uploaded and indexed successfully!")
