import unittest
import io
import pypdf
from pdf_processor import PDFProcessor
from qa_engine import QAEngine


class TestPDFQAEngine(unittest.TestCase):
    """Test suite for PDF Processor and QA Engine."""

    def setUp(self):
        self.processor = PDFProcessor(chunk_size=300, chunk_overlap=50)
        self.qa_engine = QAEngine()

    def _create_sample_pdf_bytes(self) -> io.BytesIO:
        """Helper to create an in-memory PDF with sample text."""
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=612, height=792)
        
        # We test with synthetic page text directly using processor format
        pdf_stream = io.BytesIO()
        writer.write(pdf_stream)
        pdf_stream.seek(0)
        return pdf_stream

    def test_chunking_and_indexing(self):
        sample_pages = [
            {
                "page_num": 1,
                "text": "Artificial Intelligence is transforming software development. Machine Learning models process data quickly."
            },
            {
                "page_num": 2,
                "text": "PDF question answering system uses RAG architecture. Retrieval Augmented Generation matches user query to document chunks."
            }
        ]

        chunks = self.processor.create_chunks(sample_pages)
        self.assertGreater(len(chunks), 0)
        self.assertEqual(chunks[0]["page_num"], 1)

        self.qa_engine.build_index(chunks)
        results = self.qa_engine.retrieve_context("What is RAG architecture?", top_k=2)
        
        self.assertGreater(len(results), 0)
        self.assertIn("RAG", results[0]["text"])

    def test_answer_generation_extractive(self):
        sample_pages = [
            {
                "page_num": 1,
                "text": "The solar system consists of eight planets. Jupiter is the largest planet in our solar system."
            }
        ]
        chunks = self.processor.create_chunks(sample_pages)
        self.qa_engine.build_index(chunks)
        retrieved = self.qa_engine.retrieve_context("Which is the largest planet?", top_k=2)

        res = self.qa_engine.answer_question("Which is the largest planet?", retrieved)
        self.assertIn("answer", res)
        self.assertIn("Jupiter", res["answer"])
        self.assertEqual(len(res["context_chunks"]), len(retrieved))

    def test_summary_generation(self):
        sample_pages = [
            {
                "page_num": 1,
                "text": "Overview of Data Science\nData science involves statistics and programming."
            }
        ]
        summary = self.processor.get_document_summary(sample_pages)
        self.assertEqual(summary["total_pages"], 1)
        self.assertGreater(summary["total_words"], 0)


if __name__ == "__main__":
    unittest.main()
