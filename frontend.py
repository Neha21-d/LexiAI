import streamlit as st
import time
from vector_database import index_pdf, upload_pdf
from rag_pipeline import (
    answer_query,
    retrieve_docs,
    llm_model,
    summarize_document,
    generate_report
)

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="LexiAI",
    page_icon="⚖️",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

st.markdown("""
<style>

    body {
        background-color: #0E1117;
        color: #E0E0E0;
        font-family: Arial, sans-serif;
    }

    .stTextArea textarea {
        font-size: 16px;
        border-radius: 12px;
        padding: 12px;
        border: 2px solid #D4AF37;
        background-color: #1E1E1E;
        color: white;
    }

    .stButton button {
        background-color: #D4AF37;
        color: black;
        border-radius: 12px;
        padding: 12px 25px;
        font-size: 16px;
        font-weight: bold;
        transition: 0.3s;
        box-shadow: 0px 4px 10px rgba(212, 175, 55, 0.3);
    }

    .stButton button:hover {
        background-color: #B8860B;
        color: white;
    }

    .stChatMessage {
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        background-color: #1E1E1E;
        box-shadow: 2px 2px 10px rgba(255,255,255,0.1);
        color: #E0E0E0;
    }

    .summary-box {
        background-color: #1E1E1E;
        padding: 15px;
        border-left: 5px solid #D4AF37;
        color: #E0E0E0;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(212, 175, 55, 0.3);
    }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

if "user_queries" not in st.session_state:
    st.session_state.user_queries = []

if "ai_responses" not in st.session_state:
    st.session_state.ai_responses = []

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:

    st.title("⚖️ LexiAI")

    st.success("⚡ Powered by RAG + Vector Search")

    st.markdown("---")

    st.markdown("## 🚀 Features")

    st.markdown("""
    ✅ Contract Summarization  
    ✅ Legal Risk Detection  
    ✅ Clause Extraction  
    ✅ AI Legal Q&A  
    ✅ Legal Keyword Detection  
    ✅ AI Report Generation  
    """)

    st.markdown("---")

    st.markdown("## 🛠 Tech Stack")

    st.markdown("""
    - LangChain
    - FAISS Vector DB
    - Streamlit
    - Groq API (Llama 3.3 70B)
    - RAG Architecture
    """)

    st.markdown("---")

    st.info("Built using Retrieval-Augmented Generation")

    st.markdown("---")

    st.markdown("## 🕘 Recent Questions")

    if len(st.session_state.user_queries) > 0:

        for q in st.session_state.user_queries[-5:]:

            st.write("•", q)

    else:
        st.write("No questions asked yet.")

# ---------------------------------------------------
# MAIN HEADING
# ---------------------------------------------------

st.markdown("""
<h1 style='text-align: center; color: #D4AF37;'>
⚖️ LexiAI – Smart Legal Document Analyzer
</h1>

<p style='text-align: center; font-size:18px; color:#E0E0E0;'>
AI-powered legal contract analysis using RAG, vector search, and LLMs.
Upload legal documents and get intelligent summaries, clause analysis,
risk detection, and contextual AI-powered answers.
</p>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# FEATURE CARDS
# ---------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.info("📄 Summarize Contracts")

with col2:
    st.warning("⚠️ Detect Legal Risks")

with col3:
    st.success("🤖 AI Legal Assistant")

# ---------------------------------------------------
# UPLOAD SECTION
# ---------------------------------------------------

st.markdown("## 📂 Upload Legal Contract")

uploaded_file = st.file_uploader(
    "Upload a legal document (PDF)",
    type="pdf",
    accept_multiple_files=False
)

# ---------------------------------------------------
# PROCESS PDF
# ---------------------------------------------------

if uploaded_file:

    st.success(f"📄 Uploaded: {uploaded_file.name}")

    # Save + Index PDF
    file_path = upload_pdf(uploaded_file)
    index_pdf(file_path)

    # ---------------------------------------------------
    # SUMMARIZATION
    # ---------------------------------------------------

    if st.button("📜 Summarize Document"):

        with st.spinner("🔍 Generating summary..."):

            progress = st.progress(0)

            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)

            retrieved_docs = retrieve_docs(
                "Summarize this document",
                uploaded_file.name
            )

            if not retrieved_docs:

                st.error("❌ No content retrieved.")

            else:

                summary = summarize_document(retrieved_docs)

                st.markdown("### 📝 Document Summary")

                st.markdown(
                    f"<div class='summary-box'>{summary.content}</div>",
                    unsafe_allow_html=True
                )

    # ---------------------------------------------------
    # RISK ANALYZER
    # ---------------------------------------------------

    if st.button("⚠️ Analyze Risk Clauses"):

        risky_words = [
            "penalty",
            "termination",
            "liability",
            "breach",
            "compensation"
        ]

        retrieved_docs = retrieve_docs(
            "Find risky clauses",
            uploaded_file.name
        )

        risk_results = []

        for doc in retrieved_docs:

            text = doc.page_content.lower()

            for word in risky_words:

                if word in text:
                    risk_results.append(doc.page_content)
                    break

        if risk_results:

            risk_count = len(risk_results)

            if risk_count <= 2:

                st.success(
                    f"✅ Low Risk Contract ({risk_count} risky clauses found)"
                )

            elif risk_count <= 5:

                st.warning(
                    f"⚠️ Medium Risk Contract ({risk_count} risky clauses found)"
                )

            else:

                st.error(
                    f"🚨 High Risk Contract ({risk_count} risky clauses found)"
                )

            st.markdown("### ⚠️ Risk Clauses")

            for risk in risk_results[:5]:

                st.warning(risk)

        else:

            st.success("✅ No major risky clauses detected.")

    # ---------------------------------------------------
    # KEY LEGAL TERMS
    # ---------------------------------------------------

    if st.button("📌 Extract Key Legal Terms"):

        legal_terms = [
            "confidentiality",
            "termination",
            "payment",
            "liability",
            "agreement",
            "warranty",
            "obligation",
            "breach",
            "compensation"
        ]

        retrieved_docs = retrieve_docs(
            "Extract legal terms",
            uploaded_file.name
        )

        found_terms = []

        for doc in retrieved_docs:

            text = doc.page_content.lower()

            for term in legal_terms:

                if term in text and term not in found_terms:
                    found_terms.append(term)

        st.markdown("### 📌 Key Legal Terms Found")

        if found_terms:

            cols = st.columns(3)

            for index, term in enumerate(found_terms):

                cols[index % 3].info(term.title())

        else:

            st.warning("No important legal terms detected.")

# ---------------------------------------------------
# CHAT SECTION
# ---------------------------------------------------

st.markdown("## 💬 Ask Questions")

user_query = st.text_area(
    "Ask your legal question:",
    height=120,
    placeholder="Type your question here..."
)

# ---------------------------------------------------
# SAMPLE QUESTIONS
# ---------------------------------------------------

st.markdown("""
### 💡 Sample Questions

- What are the termination clauses?
- Is there any payment penalty?
- Summarize this agreement
- What liabilities are mentioned?
- Are there any confidentiality clauses?
""")

# ---------------------------------------------------
# AI QUERY
# ---------------------------------------------------

if st.button("⚖️ Ask LexiAI"):

    if uploaded_file:

        with st.spinner("⚡ Analyzing document and generating response..."):

            retrieved_docs = retrieve_docs(
                user_query,
                uploaded_file.name
            )

            # Progress Bar
            progress = st.progress(0)

            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)

            response = answer_query(
                documents=retrieved_docs,
                model=llm_model,
                query=user_query
            )

            # Save Chat History
            st.session_state.user_queries.append(user_query)

            st.session_state.ai_responses.append(
                response.content
            )

    else:

        st.error(
            "❌ Please upload a PDF before asking a question!"
        )

# ---------------------------------------------------
# CHAT HISTORY DISPLAY
# ---------------------------------------------------

if st.session_state.user_queries:

    st.markdown("## 💬 Conversation History")

    for i in range(len(st.session_state.user_queries)):

        st.chat_message("user").write(
            st.session_state.user_queries[i]
        )

        st.chat_message("assistant").write(
            st.session_state.ai_responses[i]
        )

# ---------------------------------------------------
# DOWNLOAD REPORT
# ---------------------------------------------------

if (
    st.session_state.user_queries and
    st.session_state.ai_responses
):

    if st.button("📥 Download Report"):

        report_path = generate_report(
            st.session_state.user_queries,
            st.session_state.ai_responses
        )

        with open(report_path, "rb") as file:

            st.download_button(
                label="📄 Download LexiAI Report",
                data=file,
                file_name="LexiAI_Report.pdf",
                mime="application/pdf"
            )

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown("---")

st.markdown(
    """
    <center>
    ⚖️ LexiAI | AI-Powered Legal Intelligence Platform
    </center>
    """,
    unsafe_allow_html=True
)