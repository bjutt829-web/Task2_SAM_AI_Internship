import os
import sys
from flask import Flask, render_template, request, jsonify

# Absolute base directory path resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from pdf_processor import PDFProcessor
from qa_engine import QAEngine

template_dir = os.path.join(BASE_DIR, "templates")
app = Flask(__name__, template_folder=template_dir)


@app.route("/")
@app.route("/<path:path>")
def index(path=None):
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_pdf():
    """Extracts text and chunks from PDF and returns them to client for stateless Vercel execution."""
    if "pdf" not in request.files:
        return jsonify({"error": "No PDF file uploaded"}), 400

    file = request.files["pdf"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        processor = PDFProcessor()
        pages_data = processor.extract_text_from_pdf(file)
        chunks = processor.create_chunks(pages_data)
        summary = processor.get_document_summary(pages_data)

        return jsonify({
            "success": True,
            "filename": file.filename,
            "total_pages": summary["total_pages"],
            "total_words": summary["total_words"],
            "sample_questions": summary["sample_questions"],
            "chunks": chunks
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/query", methods=["POST"])
def ask_question():
    """Stateless RAG query function using client-provided chunks."""
    data = request.json or {}
    question = data.get("question", "").strip()
    api_key = data.get("api_key", "").strip()
    chunks = data.get("chunks", [])

    if not question:
        return jsonify({"error": "Please enter a question"}), 400

    if not chunks:
        return jsonify({"error": "Please upload a PDF document first"}), 400

    try:
        qa_engine = QAEngine()
        qa_engine.build_index(chunks)
        
        retrieved_chunks = qa_engine.retrieve_context(question, top_k=4)
        response_data = qa_engine.answer_question(
            query=question,
            retrieved_chunks=retrieved_chunks,
            custom_api_key=api_key if api_key else None
        )

        return jsonify({
            "answer": response_data["answer"],
            "mode": response_data["mode"],
            "context_chunks": response_data["context_chunks"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
