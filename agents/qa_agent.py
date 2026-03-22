"""
Q&A Agent (Gemini Version)
Retrieval-Augmented Generation for answering medical questions
"""

from typing import Dict, List
from loguru import logger
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from services.vector_store import VectorStoreService
from services.session_manager import SessionManager
import os
import re


class QAAgent:
    """
    Specialized agent for question answering using RAG (Gemini-based)
    Maintains conversation context and memory
    """

    def __init__(self, vector_store: VectorStoreService, session_manager: SessionManager):
        self.vector_store = vector_store
        self.session_manager = session_manager
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
        logger.info("Q&A Agent (Gemini) initialized ")

    async def answer_question(self, session_id: str, question: str) -> Dict:
        """
        Answer question using STRICT RAG with conversation history
        Returns answer with inline citations and detailed source chunks
        """
        try:
            # Step 1: Retrieve relevant documents
            relevant_docs = self.vector_store.similarity_search(
                session_id, question, k=5
            )

            if not relevant_docs:
                return {
                    "answer": "I cannot find any relevant information in the uploaded documents to answer this question.",
                    "sources": [],
                    "citations": []
                }

            # Step 2: Build context with chunk IDs for citation
            context = self._build_context_with_chunk_ids(relevant_docs)
            
            # Step 3: Get conversation history
            history = self.session_manager.get_history(session_id)

            # Step 4: Generate answer with all condition
            answer = self._generate_grounded_answer(question, context, history)
            
            # Step 5: Extract and format citations from the answer
            citations = self._extract_citations_from_answer(answer, relevant_docs)
            
            # Step 6: Format answer with citation numbers
            formatted_answer = self._format_answer_with_citations(answer, citations)

            logger.info(f"Generated grounded answer with {len(citations)} citations")

            return {
                "answer": formatted_answer,
                "sources": citations,  # Detailed chunk information
                "citations": citations  # For Formating...
            }

        except Exception as e:
            logger.error(f"Error in Q&A: {str(e)}")
            raise

    def _build_context_with_chunk_ids(self, documents: List) -> str:
        """
        Build context with numbered chunks for citation tracking
        
        Format:
        [CHUNK_1] (Source: file.pdf, Page: 3, Type: text)
        Content here...
        
        [CHUNK_2] (Source: file.pdf, Page: 5, Type: table, Table #2)
        Table content...
        """
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            content = doc.page_content
            source = os.path.basename(doc.metadata.get("source", "Unknown"))
            page = doc.metadata.get("page", "N/A")
            doc_type = doc.metadata.get("type", "text")
            
            # Build chunk header with metadata
            header_parts = [f"[CHUNK_{i}]"]
            header_parts.append(f"(Source: {source}")
            header_parts.append(f"Page: {page}")
            
            # Add type-specific information
            if "table" in doc_type.lower():
                table_num = doc.metadata.get("table_index", "")
                if table_num != "":
                    header_parts.append(f"Table #{table_num + 1}")
            elif "image" in doc_type.lower() or "figure" in doc_type.lower():
                img_num = doc.metadata.get("image_index", "")
                if img_num != "":
                    header_parts.append(f"Image/Figure #{img_num + 1}")
            
            header_parts.append(f"Type: {doc_type})")
            
            chunk_header = " ".join(header_parts)
            context_parts.append(f"{chunk_header}\n{content}\n")
        
        return "\n".join(context_parts)

    def _generate_grounded_answer(self, question: str, context: str, history: List[Dict]) -> str:
        """Generate answer using Gemini LLM with context and history"""

        
        system_prompt = """You are a medical document assistant. Answer questions based on the provided context from medical documents.

        Guidelines:
        1. Answer ONLY using information explicitly stated in the provided CHUNK context and Chat History.
        2. Cite the CHUNK number for every piece of information used in your answer using this exact format:
        "information here (CHUNK_X)" — where X = chunk number.
        3. For tables: mention "Table #N from CHUNK_X"
        4. For images/figures: mention "Image/Figure #N from CHUNK_X"
        5. If the answer is found in Chat History (not in the CHUNKs), write:
        "In Chat History I got the information."
        Then provide the answer based on Chat History content.
        6. If the information is NOT found in the context or chat history, respond formally like this:
        "Apologies, but this specific information is not mentioned in the provided document or chat history. 
        However, the document discusses related details such as [summarize 2–3 relevant lines from the context and cite them properly]."
        7. Do NOT use any external knowledge or assumptions.
        8. Do NOT hallucinate. If something is not explicitly mentioned, clearly state that it is not available.
        9. Maintain a formal, concise, and citation-accurate tone throughout your response.

        CITATION EXAMPLES:
        CORRECT: "The patient's blood pressure was 140/90 mmHg (CHUNK_1)."
        CORRECT: "According to Table #2 from CHUNK_3, the heart rate was 78 bpm."
        CORRECT: "Image #1 from CHUNK_2 shows abnormal findings."
        CORRECT: "Ram is not going to BBSR (CHUNK_1) but going to Cuttack (CHUNK_2)."

        WRONG: "The patient's vitals were normal." (no citation)
        WRONG: "Based on medical knowledge..." (external knowledge)

        REMEMBER: Every factual statement needs (CHUNK_X) citation!"""

        # Build messages
        messages = [SystemMessage(content=system_prompt)]
        
        # Add recent history (last 20 turns)
        for msg in history[-20:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        # Add current question with context
        user_prompt = f"""Based on the following document chunks, answer the question with citations.

        DOCUMENT CHUNKS:
        {context}

        QUESTION: {question}

        ANSWER (Remember to cite CHUNK numbers for every fact):"""

        messages.append(HumanMessage(content=user_prompt))

        # Generate response
        response = self.llm.invoke(messages)
        return response.content


    def _extract_citations_from_answer(self, answer: str, documents: List) -> List[str]:
        """
        Extract citations from answer with FULL chunk content
        """
        citations = []
        
        # Find all CHUNK_X references
        chunk_pattern = r'CHUNK_(\d+)'
        referenced_chunks = set(re.findall(chunk_pattern, answer))
        
        for chunk_num_str in sorted(referenced_chunks):
            chunk_num = int(chunk_num_str)
            
            if 1 <= chunk_num <= len(documents):
                doc = documents[chunk_num - 1]
                
                # Extract and clean metadata
                source_raw = doc.metadata.get("source", "Unknown")
                source = self._clean_filename(source_raw)
                page = doc.metadata.get("page", "N/A")
                doc_type = doc.metadata.get("type", "text")
                
                # Get FULL content
                full_content = doc.page_content.strip()
                
                # Build citation
                citation_parts = [f"Chunk {chunk_num}"]
                citation_parts.append(f"{source} - Page {page}")
                
                # Add type-specific metadata
                type_details = []
                if "table" in doc_type.lower():
                    table_num = doc.metadata.get("table_index", "")
                    if table_num != "":
                        type_details.append(f"Table #{table_num + 1}")
                elif "image" in doc_type.lower() or "figure" in doc_type.lower():
                    img_num = doc.metadata.get("image_index", "")
                    if img_num != "":
                        type_details.append(f"Image/Figure #{img_num + 1}")
                
                type_details.append(f"Type: {doc_type}")
                citation_parts.append(", ".join(type_details))
                
                # Format with full content
                citation_header = ": ".join(citation_parts)
                citation_full = f"{citation_header}\nContent: {full_content}"
                
                citations.append(citation_full)
        
        return citations

    def _clean_filename(self, filepath: str) -> str:
        """Remove UUID prefix from filename"""
        filename = os.path.basename(filepath)
        # Remove UUID pattern: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx_
        import re
        cleaned = re.sub(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}_', '', filename)
        return cleaned if cleaned else filename


    def _format_answer_with_citations(self, answer: str, citations: List[str]) -> str:
        """
        Format the answer to replace CHUNK_X with (X) for cleaner display
        
        Example:
        "Ram is not going to BBSR (CHUNK_1)" 
        becomes 
        "Ram is not going to BBSR (1)"
        """
        # Replace CHUNK_X with just (X)
        formatted = re.sub(r'\(CHUNK_(\d+)\)', r'(\1)', answer)
        formatted = re.sub(r'CHUNK_(\d+)', r'(\1)', formatted)
        
        return formatted

    def _build_context(self, documents: List) -> str:
        context_parts = []
        for i, doc in enumerate(documents, 1):
            content = doc.page_content
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "")
            page_info = f" (Page {page})" if page else ""
            context_parts.append(f"[Document {i} from {source}{page_info}]\n{content}\n")
        return "\n".join(context_parts)

    def _extract_sources(self, documents: List) -> List[str]:
        sources = set()
        for doc in documents:
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "")
            if page:
                sources.add(f"{source} (Page {page})")
            else:
                sources.add(source)
        return list(sources)