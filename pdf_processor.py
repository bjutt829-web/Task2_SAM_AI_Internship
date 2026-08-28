import io
import re
from typing import List, Dict, Any, Tuple
import pypdf


class PDFProcessor:
    """Handles PDF reading, text extraction, and text chunking with page tracking."""

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 120):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_text_from_pdf(self, pdf_file) -> List[Dict[str, Any]]:
        """
        Extracts text page by page from a PDF file.
        Accepts file path (str), BytesIO, or uploaded file object.
        Returns a list of dicts: [{'page_num': 1, 'text': '...'}, ...]
        """
        pages_data = []
        
        if isinstance(pdf_file, str):
            reader = pypdf.PdfReader(pdf_file)
        elif hasattr(pdf_file, "read"):
            # If it's a file stream or Streamlit UploadedFile
            if hasattr(pdf_file, "seek"):
                pdf_file.seek(0)
            file_content = pdf_file.read()
            if hasattr(pdf_file, "seek"):
                pdf_file.seek(0)
            pdf_bytes = io.BytesIO(file_content)
            reader = pypdf.PdfReader(pdf_bytes)
        else:
            raise ValueError("Unsupported PDF file format provided.")

        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            # Clean text lightly while keeping sentence structure
            cleaned_text = self._clean_text(text)
            pages_data.append({
                "page_num": i + 1,
                "text": cleaned_text
            })

        return pages_data

    def create_chunks(self, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Splits extracted pages text into semantic overlapping chunks while preserving page numbers.
        Returns list of dicts: [{'chunk_id': 0, 'page_num': 1, 'text': '...', 'start_char': 0}]
        """
        chunks = []
        chunk_id = 0

        for page in pages_data:
            page_num = page["page_num"]
            text = page["text"]

            if not text.strip():
                continue

            # Split text into paragraphs or sentences first if possible
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            current_chunk = ""
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 <= self.chunk_size:
                    if current_chunk:
                        current_chunk += " " + sentence
                    else:
                        current_chunk = sentence
                else:
                    if current_chunk.strip():
                        chunks.append({
                            "chunk_id": chunk_id,
                            "page_num": page_num,
                            "text": current_chunk.strip()
                        })
                        chunk_id += 1

                    # Overlap handling: take last N characters for overlap
                    overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                    current_chunk = overlap_text + " " + sentence if overlap_text else sentence

            if current_chunk.strip():
                chunks.append({
                    "chunk_id": chunk_id,
                    "page_num": page_num,
                    "text": current_chunk.strip()
                })
                chunk_id += 1

        return chunks

    def get_document_summary(self, pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates document summary stats."""
        total_pages = len(pages_data)
        full_text = " ".join(p["text"] for p in pages_data)
        words = full_text.split()
        total_words = len(words)
        
        # Generate sample questions based on extracted key sentences
        sample_questions = self._generate_sample_questions(full_text)

        return {
            "total_pages": total_pages,
            "total_words": total_words,
            "sample_questions": sample_questions,
            "preview_snippet": full_text[:300] + "..." if len(full_text) > 300 else full_text
        }

    def _clean_text(self, text: str) -> str:
        """Clean excessive whitespaces and non-printable characters."""
        text = re.sub(r'[\r\n]+', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()

    def _generate_sample_questions(self, text: str) -> List[str]:
        """Auto-generates relevant sample questions from document headers or key sentences."""
        questions = []
        # Look for headings or bold lines
        lines = text.split('\n')
        for line in lines:
            line_str = line.strip()
            if len(line_str) > 10 and len(line_str) < 80 and not line_str.endswith('.'):
                questions.append(f"What does the document say about '{line_str}'?")
            if len(questions) >= 3:
                break
        
        # Default fallback questions if no headings found
        if not questions:
            questions = [
                "What is the main topic of this document?",
                "Can you summarize the key findings or points?",
                "What are the primary recommendations or conclusions?"
            ]
        return questions
