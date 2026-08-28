import os
from fpdf import FPDF

def generate_sample_pdf():
    os.makedirs("sample_documents", exist_ok=True)
    pdf_path = os.path.join("sample_documents", "AI_Technology_Overview.pdf")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Page 1: Executive Summary & RAG Architecture
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, "Artificial Intelligence & RAG Technology Report", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 8, "1. Executive Summary", ln=True)
    
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(51, 65, 85)
    summary_text = (
        "Artificial Intelligence (AI) has revolutionized how organizations handle unstructured text documents. "
        "Retrieval-Augmented Generation (RAG) combines search retrieval algorithms with generative Large Language Models (LLMs) "
        "to deliver grounded, accurate, and verifiable answers from proprietary PDF documents and knowledge bases."
    )
    pdf.multi_cell(0, 6, summary_text)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 8, "2. How Question Answering Works", ln=True)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(51, 65, 85)
    qa_text = (
        "The PDF Question Answering engine operates through three main stages:\n"
        "1. Document Ingestion & Chunking: PDF files are parsed into semantic text passages while tracking page numbers.\n"
        "2. Vector Indexing: Text chunks are converted into numerical representations using TF-IDF or vector embeddings.\n"
        "3. Context Retrieval & Answer Generation: When a user asks a question, top matching context chunks are retrieved "
        "and passed to the AI model to generate a precise answer with source citations."
    )
    pdf.multi_cell(0, 6, qa_text)

    # Page 2: Key Features & Applications
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 8, "3. Key System Features", ln=True)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(51, 65, 85)
    features_text = (
        "- Page-Level Citations: Users can verify exact page numbers for every extracted fact.\n"
        "- Dual Execution Modes: Supports offline extractive answering as well as cloud-based Gemini LLM generation.\n"
        "- Interactive UI: Built with Streamlit for clean document metrics and interactive conversation history."
    )
    pdf.multi_cell(0, 6, features_text)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 8, "4. Recommendations & Future Outlook", ln=True)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(51, 65, 85)
    rec_text = (
        "Organizations adopting AI PDF QA systems should ensure proper document OCR pre-processing for scanned PDFs, "
        "implement chunk size optimization, and enforce security policies around document privacy."
    )
    pdf.multi_cell(0, 6, rec_text)

    pdf.output(pdf_path)
    print(f"Sample PDF successfully created at: {pdf_path}")

if __name__ == "__main__":
    generate_sample_pdf()
