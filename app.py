import streamlit as st
import os
import time
from pdf_processor import PDFProcessor
from qa_engine import QAEngine

# Page Configuration
st.set_page_config(
    page_title="Task 2 Sam AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS matching the uploaded soft pastel gradient & TASK 2 prompt styling
st.markdown("""
<style>
    /* Soft Pastel Mesh Background matching sample theme */
    .stApp {
        background: linear-gradient(135deg, #E6F4F1 0%, #E0F2FE 45%, #F3E8FF 85%, #FCF4FF 100%) !important;
        background-attachment: fixed !important;
    }

    /* Floating Pastel Dots effect using background images */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none;
        background-image: 
            radial-gradient(circle at 25% 20%, rgba(52, 211, 153, 0.5) 0, rgba(52, 211, 153, 0.5) 7px, transparent 8px),
            radial-gradient(circle at 18% 48%, rgba(56, 189, 248, 0.6) 0, rgba(56, 189, 248, 0.6) 10px, transparent 11px),
            radial-gradient(circle at 60% 88%, rgba(192, 132, 252, 0.5) 0, rgba(192, 132, 252, 0.5) 9px, transparent 10px),
            radial-gradient(circle at 95% 65%, rgba(45, 212, 191, 0.6) 0, rgba(45, 212, 191, 0.6) 8px, transparent 9px);
        z-index: 0;
    }
    
    /* Ensure all Markdown text is crisp and readable */
    .stMarkdown p, .stMarkdown li, .stMarkdown span, h1, h2, h3, h4, h5, h6 {
        color: #0F172A !important;
    }

    /* Top Task Header Banner matching Task 2 Prompt */
    .task-banner {
        background: linear-gradient(135deg, #008B99 0%, #00A8B5 100%) !important;
        padding: 24px 32px !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 139, 153, 0.3) !important;
        margin-bottom: 24px !important;
        text-align: center !important;
        position: relative !important;
        overflow: hidden !important;
    }
    .task-banner .task-title {
        font-size: 2.3rem !important;
        font-weight: 800 !important;
        letter-spacing: 1px !important;
        margin: 0 !important;
        color: #FFFFFF !important;
        text-transform: uppercase !important;
    }
    .task-banner .task-sub {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        margin-top: 6px !important;
        color: #FF5252 !important; /* Vivid Red matching prompt text */
        background-color: #FFFFFF !important;
        display: inline-block !important;
        padding: 4px 18px !important;
        border-radius: 20px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }

    /* Sidebar Frosted Glass Styling */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.92) !important;
        backdrop-filter: blur(10px) !important;
        border-right: 1px solid rgba(226, 232, 240, 0.8) !important;
    }
    section[data-testid="stSidebar"] * {
        color: #0F172A !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] label {
        color: #334155 !important;
        font-weight: 600 !important;
    }

    /* FILE UPLOADER WIDGET FIXES (Removes pitch black background) */
    [data-testid="stFileUploader"], [data-testid="stFileUploader"] section {
        background-color: #F8FAFC !important;
        border: 2px dashed #00A8B5 !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }
    [data-testid="stFileUploader"] * {
        color: #0F172A !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: #00A8B5 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    [data-testid="stFileUploader"] button * {
        color: #FFFFFF !important;
    }

    /* TEXT INPUT FIXES (Gemini API Key, etc) */
    [data-testid="stTextInput"] input, input[type="text"], input[type="password"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
    }

    /* CHAT INPUT FIXES */
    [data-testid="stChatInput"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #0F172A !important;
        background-color: transparent !important;
    }

    /* EXPANDER FIXES */
    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
    }

    /* Elegant Content Cards */
    .welcome-card {
        background: rgba(255, 255, 255, 0.92) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        border-radius: 16px !important;
        padding: 22px !important;
        height: 100% !important;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.06) !important;
    }
    .welcome-card h3 {
        color: #008B99 !important;
        font-size: 1.18rem !important;
        margin-top: 0 !important;
        margin-bottom: 8px !important;
    }
    .welcome-card p {
        color: #475569 !important;
        font-size: 0.96rem !important;
        margin: 0 !important;
    }

    /* Document Statistic Cards */
    .stat-card-pages {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%) !important;
        border: 1px solid #A7F3D0 !important;
        border-radius: 12px !important;
        padding: 12px !important;
        text-align: center !important;
    }
    .stat-card-pages * {
        color: #065F46 !important;
        font-weight: 700 !important;
    }
    
    .stat-card-words {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%) !important;
        border: 1px solid #FDE68A !important;
        border-radius: 12px !important;
        padding: 12px !important;
        text-align: center !important;
    }
    .stat-card-words * {
        color: #92400E !important;
        font-weight: 700 !important;
    }

    /* Context Cards (PDF Citations) */
    .context-card {
        background: #FFFFFF !important;
        color: #0F172A !important;
        border: 1.5px solid #CBD5E1 !important;
        border-left: 6px solid #00A8B5 !important;
        padding: 18px 22px !important;
        margin-top: 10px !important;
        margin-bottom: 14px !important;
        border-radius: 12px !important;
        font-size: 0.96rem !important;
        line-height: 1.6 !important;
        box-shadow: 0 8px 20px -4px rgba(0, 139, 153, 0.12) !important;
    }
    .context-card * {
        color: #0F172A !important;
    }
    
    .page-badge {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        padding: 4px 14px !important;
        border-radius: 20px !important;
        font-size: 0.82rem !important;
        display: inline-block !important;
    }
    
    .score-badge {
        background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        padding: 4px 14px !important;
        border-radius: 20px !important;
        font-size: 0.82rem !important;
        float: right !important;
    }

    /* Interactive Buttons */
    .stButton>button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: 1px solid #CBD5E1 !important;
        background: #FFFFFF !important;
        color: #0F172A !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        border-color: #00A8B5 !important;
        color: #00A8B5 !important;
        transform: translateY(-1px) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session States
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_data" not in st.session_state:
    st.session_state.pdf_data = None

if "qa_engine" not in st.session_state:
    st.session_state.qa_engine = None

if "processor" not in st.session_state:
    st.session_state.processor = PDFProcessor()

if "doc_summary" not in st.session_state:
    st.session_state.doc_summary = None


# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/pdf-2.png", width=64)
    st.title("Task 2 Sam AI")
    st.write("Upload a PDF to ask questions and extract precise answers.")

    # PDF File Upload
    uploaded_file = st.file_uploader(
        "Upload PDF Document",
        type=["pdf"],
        help="Upload any PDF file to start asking questions."
    )

    st.markdown("---")

    # API Configuration
    st.subheader("⚙️ Engine Settings")
    api_key_input = st.text_input(
        "Gemini API Key (Optional)",
        type="password",
        help="Enter your Google Gemini API key for deep generative synthesis. Leaves empty to use offline extractive mode."
    )

    top_k_chunks = st.slider(
        "Context Passages (Top-K)",
        min_value=1,
        max_value=8,
        value=4,
        help="Number of document text passages retrieved for answering."
    )

    st.markdown("---")

    # Document Statistics (when loaded)
    if st.session_state.doc_summary:
        st.subheader("📊 Document Insights")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"""
                <div class="stat-card-pages">
                    <span style="font-size:0.75rem;">TOTAL PAGES</span><br/>
                    <span style="font-size:1.3rem;">{st.session_state.doc_summary['total_pages']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"""
                <div class="stat-card-words">
                    <span style="font-size:0.75rem;">TOTAL WORDS</span><br/>
                    <span style="font-size:1.15rem;">{st.session_state.doc_summary['total_words']:,}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br/>**Sample Questions:**", unsafe_allow_html=True)
        for q in st.session_state.doc_summary["sample_questions"]:
            if st.button(f"❓ {q[:38]}...", key=q, help=q, use_container_width=True):
                st.session_state["preset_query"] = q

        st.markdown("---")

    # Reset Button
    if st.button("🗑️ Clear Chat & Reset", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pdf_data = None
        st.session_state.doc_summary = None
        st.session_state.qa_engine = None
        st.rerun()


# --- PROCESS UPLOADED PDF ---
if uploaded_file is not None:
    # Check if this is a new upload
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    if st.session_state.get("current_file_id") != file_id:
        with st.spinner("Processing & indexing PDF document..."):
            try:
                processor = PDFProcessor()
                pages_data = processor.extract_text_from_pdf(uploaded_file)
                chunks = processor.create_chunks(pages_data)
                
                qa_engine = QAEngine(api_key=api_key_input)
                qa_engine.build_index(chunks)

                st.session_state.processor = processor
                st.session_state.qa_engine = qa_engine
                st.session_state.doc_summary = processor.get_document_summary(pages_data)
                st.session_state.current_file_id = file_id
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": f"✅ Successfully processed **{uploaded_file.name}** ({st.session_state.doc_summary['total_pages']} pages, {st.session_state.doc_summary['total_words']:,} words).\n\nAsk me any question about the contents of this document!",
                        "context": []
                    }
                ]
                st.success("Document indexed successfully!")
            except Exception as e:
                st.error(f"Failed to process PDF: {e}")


# --- MAIN HEADER BANNER MATCHING TASK 2 PROMPT ---
st.markdown(
    """
    <div class="task-banner">
        <div class="task-title">TASK 2 SAM AI</div>
        <div class="task-sub">AI PDF Question Answering</div>
    </div>
    """,
    unsafe_allow_html=True
)


# --- WELCOME BANNER (IF NO FILE UPLOADED) ---
if uploaded_file is None:
    st.info("👈 Please upload a PDF document in the sidebar to begin!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="welcome-card">
                <h3>📄 Upload PDF Document</h3>
                <p>Upload reports, contracts, academic papers, or manuals directly from the sidebar.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div class="welcome-card">
                <h3>❓ Ask Questions</h3>
                <p>Query specific facts, summaries, key metrics, or data points from your document.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            """
            <div class="welcome-card">
                <h3>📌 Display Response with Context</h3>
                <p>Extract relevant answers with exact page numbers and context snippets.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br/>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class="welcome-card">
            <h3>🌟 User-Friendly Interface & Features</h3>
            <p style="margin-bottom:8px;">• <b>Smart Vector Search:</b> Automatically indexes text passages using TF-IDF & Cosine Similarity.</p>
            <p style="margin-bottom:8px;">• <b>Page-by-Page Citations:</b> Displays exact page numbers where information was extracted.</p>
            <p style="margin-bottom:8px;">• <b>Dual AI Answering Engine:</b> Works offline using contextual extraction or with Google Gemini for rich summaries.</p>
            <p>• <b>Interactive UI:</b> Responsive pastel theme designed for seamless PDF exploration.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()


# --- CHAT DISPLAY & QA INTERFACE ---

# Preset query trigger from sidebar sample questions
preset_query = st.session_state.pop("preset_query", None)

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display Context Expander if available
        if message.get("context"):
            with st.expander("📌 Extracted Source Context (PDF Citations)", expanded=False):
                for chunk in message["context"]:
                    st.markdown(
                        f"""
                        <div class="context-card">
                            <span class="page-badge">Page {chunk['page_num']}</span>
                            <span class="score-badge">Relevance: {chunk.get('similarity_score', 0):.2f}</span>
                            <br/><br/>
                            {chunk['text']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


# User Input Box
user_query = st.chat_input("Ask a question about your PDF document...") or preset_query

if user_query:
    # Add User Message to Chat
    st.session_state.messages.append({"role": "user", "content": user_query, "context": []})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Process Question via QA Engine
    with st.chat_message("assistant"):
        with st.spinner("Searching document context and generating answer..."):
            qa_engine: QAEngine = st.session_state.qa_engine
            
            # 1. Retrieve Context
            retrieved_chunks = qa_engine.retrieve_context(user_query, top_k=top_k_chunks)
            
            # 2. Answer Question
            response_data = qa_engine.answer_question(
                query=user_query,
                retrieved_chunks=retrieved_chunks,
                custom_api_key=api_key_input
            )

            answer = response_data["answer"]
            mode = response_data["mode"]
            context_chunks = response_data["context_chunks"]

            # Display Answer & Mode Badge
            st.markdown(answer)
            st.caption(f"Engine Mode: **{mode}**")

            # Display Extracted Context
            if context_chunks:
                with st.expander("📌 Extracted Source Context (PDF Citations)", expanded=True):
                    for chunk in context_chunks:
                        st.markdown(
                            f"""
                            <div class="context-card">
                                <span class="page-badge">Page {chunk['page_num']}</span>
                                <span class="score-badge">Relevance: {chunk.get('similarity_score', 0):.2f}</span>
                                <br/><br/>
                                {chunk['text']}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            # Store in Chat History
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "context": context_chunks
            })
