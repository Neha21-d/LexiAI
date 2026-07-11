import os
import streamlit as st

from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq

st.set_page_config(page_title="LexiAI", page_icon="⚖️")
st.title("⚖️ LexiAI - AI Lawyer")
st.write("Upload a PDF and ask questions based on its content.")

custom_prompt_template = """
Use the pieces of information provided in the context to answer the user's question.
If you don't know the answer, just say that you don't know.
Do not make up an answer.
Only answer from the given context.

Question: {question}
Context: {context}
Answer:
"""

pdfs_directory = "pdfs"
FAISS_DB_PATH = "vectorstore/db_faiss"
ollama_model_name = "nomic-embed-text"

import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

os.makedirs(pdfs_directory, exist_ok=True)
os.makedirs("vectorstore", exist_ok=True)

embeddings = OllamaEmbeddings(model=ollama_model_name)

llm_model = ChatGroq(
    model="deepseek-r1-distill-llama-70b",
    api_key=groq_api_key
)

def upload_pdf(file):
    file_path = os.path.join(pdfs_directory, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    return file_path

def load_pdf(file_path):
    loader = PDFPlumberLoader(file_path)
    documents = loader.load()
    return documents

def create_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    text_chunks = text_splitter.split_documents(documents)
    return text_chunks

def get_embedding_model(model_name):
    return OllamaEmbeddings(model=model_name)

def create_vector_store(db_faiss_path, text_chunks, model_name):
    faiss_db = FAISS.from_documents(
        text_chunks,
        get_embedding_model(model_name)
    )
    faiss_db.save_local(db_faiss_path)
    return faiss_db

def retrieve_docs(faiss_db, query):
    return faiss_db.similarity_search(query, k=4)

def get_context(documents):
    return "\n\n".join([doc.page_content for doc in documents])

def answer_query(documents, model, query):
    context = get_context(documents)
    prompt = ChatPromptTemplate.from_template(custom_prompt_template)
    chain = prompt | model
    response = chain.invoke({"question": query, "context": context})
    return response.content if hasattr(response, "content") else str(response)

uploaded_file = st.file_uploader(
    "Upload PDF",
    type="pdf",
    accept_multiple_files=False
)

user_query = st.text_area(
    "Enter your prompt:",
    height=150,
    placeholder="Ask anything from the uploaded PDF..."
)

ask_question = st.button("Ask AI Lawyer")

if ask_question:
    if uploaded_file and user_query.strip():
        try:
            with st.spinner("Processing PDF and generating answer..."):
                saved_pdf_path = upload_pdf(uploaded_file)
                documents = load_pdf(saved_pdf_path)
                text_chunks = create_chunks(documents)
                faiss_db = create_vector_store(
                    FAISS_DB_PATH,
                    text_chunks,
                    ollama_model_name
                )
                retrieved_docs = retrieve_docs(faiss_db, user_query)
                response = answer_query(
                    documents=retrieved_docs,
                    model=llm_model,
                    query=user_query
                )

            st.chat_message("user").write(user_query)
            st.chat_message("assistant").write(response)

        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.error("Kindly upload a valid PDF file and enter a valid question.")