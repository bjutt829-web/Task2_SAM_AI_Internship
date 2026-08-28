import os
import re
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class QAEngine:
    """RAG Question Answering engine using TF-IDF retrieval and Gemini AI / Contextual synthesis."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.chunks: List[Dict[str, Any]] = []

    def build_index(self, chunks: List[Dict[str, Any]]):
        """Indexes text chunks using TF-IDF Vectorizer for fast similarity search."""
        self.chunks = chunks
        if not chunks:
            self.vectorizer = None
            self.tfidf_matrix = None
            return

        corpus = [c["text"] for c in chunks]
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def retrieve_context(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Retrieves top_k relevant text chunks for a given query."""
        if not self.vectorizer or self.tfidf_matrix is None or not self.chunks:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            # Only include chunks with non-zero similarity or top matches
            if score > 0.01 or len(results) == 0:
                chunk_copy = dict(self.chunks[idx])
                chunk_copy["similarity_score"] = round(score, 4)
                results.append(chunk_copy)

        return results

    def answer_question(self, query: str, retrieved_chunks: List[Dict[str, Any]], custom_api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates answer for query given retrieved context chunks.
        Uses Gemini LLM if API key is provided, else falls back to Smart Contextual Extractive Generator.
        """
        effective_key = custom_api_key or self.api_key

        context_text = "\n\n".join([
            f"[Page {c['page_num']}] {c['text']}" for c in retrieved_chunks
        ])

        if not context_text.strip():
            return {
                "answer": "I couldn't find any relevant information in the uploaded PDF to answer this question.",
                "context_chunks": [],
                "mode": "no_context"
            }

        # Try Gemini API if key is available
        if effective_key:
            try:
                llm_response = self._generate_gemini_answer(query, context_text, effective_key)
                if llm_response:
                    return {
                        "answer": llm_response,
                        "context_chunks": retrieved_chunks,
                        "mode": "Gemini AI"
                    }
            except Exception as e:
                print(f"Gemini API call failed, falling back to extractive engine: {e}")

        # Fallback to Smart Extractive Synthesis Mode
        extractive_answer = self._generate_extractive_answer(query, retrieved_chunks)
        return {
            "answer": extractive_answer,
            "context_chunks": retrieved_chunks,
            "mode": "Smart Contextual Extraction (Offline)"
        }

    def _generate_gemini_answer(self, query: str, context_text: str, api_key: str) -> Optional[str]:
        """Uses Google Gemini API to generate concise response based strictly on context."""
        prompt = (
            "You are an AI assistant answering questions based strictly on the provided PDF document context.\n"
            "Guidelines:\n"
            "1. Answer the question accurately using ONLY the context provided below.\n"
            "2. If the answer cannot be determined from the context, state clearly that the document does not contain this information.\n"
            "3. Reference page numbers where appropriate (e.g., [Page X]).\n\n"
            f"DOCUMENT CONTEXT:\n{context_text}\n\n"
            f"QUESTION: {query}\n\n"
            "ANSWER:"
        )

        # Attempt using google.genai or google.generativeai
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text.strip()
        except Exception:
            try:
                import google.generativeai as genai_legacy
                genai_legacy.configure(api_key=api_key)
                model = genai_legacy.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                raise e

    def _generate_extractive_answer(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        """Constructs an extractive summary answer from top matching sentences across chunks."""
        query_words = set(re.findall(r'\w+', query.lower())) - {'what', 'is', 'the', 'how', 'why', 'who', 'where', 'are', 'in', 'on', 'of', 'and', 'a', 'an', 'to', 'for'}

        best_sentences = []
        seen_sentences = set()

        for chunk in chunks:
            page_num = chunk["page_num"]
            sentences = re.split(r'(?<=[.!?])\s+', chunk["text"])
            
            for sent in sentences:
                sent_clean = sent.strip()
                if not sent_clean or sent_clean in seen_sentences:
                    continue
                
                # Count word overlap with query
                sent_words = set(re.findall(r'\w+', sent_clean.lower()))
                overlap = len(query_words.intersection(sent_words))

                if overlap > 0 or len(best_sentences) < 2:
                    seen_sentences.add(sent_clean)
                    best_sentences.append((overlap, page_num, sent_clean))

        # Sort by overlap score descending
        best_sentences.sort(key=lambda x: x[0], reverse=True)

        if not best_sentences:
            return "Based on the PDF context retrieved, no direct sentence matches were found for your query."

        # Take top sentences and format response
        top_items = best_sentences[:3]
        formatted_parts = []

        for _, page_num, sent in top_items:
            formatted_parts.append(f"• **[Page {page_num}]** {sent}")

        answer = (
            f"Here are the relevant details extracted directly from the document context:\n\n"
            + "\n\n".join(formatted_parts)
            + "\n\n*(Note: For enhanced generative summaries, you can provide a Gemini API Key in the sidebar.)*"
        )
        return answer
