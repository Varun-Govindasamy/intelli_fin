import os
import re
import asyncio
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from openai import OpenAI
from sentence_transformers import CrossEncoder
import numpy as np
from dotenv import load_dotenv
from app.services.guardrails_service import guardrails_service

load_dotenv()


class ContentMetadataExtractor:
    """Extract structured metadata from document content (dates, amounts, categories)"""
    
    # Month name mappings
    MONTH_NAMES = {
        'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
        'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6,
        'july': 7, 'jul': 7, 'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'sept': 9,
        'october': 10, 'oct': 10, 'november': 11, 'nov': 11, 'december': 12, 'dec': 12
    }
    
    # Financial categories keywords
    CATEGORY_KEYWORDS = {
        'travel': ['travel', 'flight', 'hotel', 'airfare', 'trip', 'transportation', 'uber', 'taxi'],
        'food': ['food', 'restaurant', 'dining', 'meal', 'lunch', 'dinner', 'breakfast', 'groceries'],
        'utilities': ['utilities', 'electricity', 'water', 'gas', 'internet', 'phone', 'bill'],
        'salary': ['salary', 'wage', 'payroll', 'compensation', 'income'],
        'rent': ['rent', 'lease', 'housing', 'apartment'],
        'insurance': ['insurance', 'premium', 'coverage', 'policy'],
        'healthcare': ['healthcare', 'medical', 'hospital', 'doctor', 'pharmacy', 'health'],
        'entertainment': ['entertainment', 'movie', 'subscription', 'netflix', 'spotify', 'gaming'],
        'shopping': ['shopping', 'purchase', 'amazon', 'retail', 'clothes', 'electronics'],
        'investment': ['investment', 'stock', 'bond', 'mutual fund', 'dividend', 'portfolio'],
        'tax': ['tax', 'taxes', 'irs', 'deduction', 'refund'],
        'education': ['education', 'tuition', 'course', 'training', 'school', 'university'],
        'miscellaneous': ['miscellaneous', 'misc', 'other', 'general']
    }
    
    @classmethod
    def extract_years(cls, text: str) -> List[int]:
        """Extract all 4-digit years from text (1900-2099)"""
        years = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
        return list(set(int(y) for y in years))
    
    @classmethod
    def extract_months(cls, text: str) -> List[int]:
        """Extract months from text (both names and numbers)"""
        months = set()
        
        # Match month names
        text_lower = text.lower()
        for month_name, month_num in cls.MONTH_NAMES.items():
            if re.search(r'\b' + month_name + r'\b', text_lower):
                months.add(month_num)
        
        # Match numeric months in date patterns (MM/DD, DD/MM, YYYY-MM, etc.)
        # Pattern: MM/DD/YYYY or DD/MM/YYYY
        date_patterns = re.findall(r'\b(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})\b', text)
        for p in date_patterns:
            m1, m2 = int(p[0]), int(p[1])
            if 1 <= m1 <= 12:
                months.add(m1)
            if 1 <= m2 <= 12:
                months.add(m2)
        
        # Pattern: YYYY-MM-DD
        iso_dates = re.findall(r'\b\d{4}-(\d{2})-\d{2}\b', text)
        for m in iso_dates:
            month = int(m)
            if 1 <= month <= 12:
                months.add(month)
        
        return list(months)
    
    @classmethod
    def extract_days(cls, text: str) -> List[int]:
        """Extract day numbers from date patterns"""
        days = set()
        
        # Pattern: various date formats
        date_patterns = re.findall(r'\b(\d{1,2})[/\-](\d{1,2})[/\-]\d{2,4}\b', text)
        for p in date_patterns:
            d1, d2 = int(p[0]), int(p[1])
            if 1 <= d1 <= 31:
                days.add(d1)
            if 1 <= d2 <= 31:
                days.add(d2)
        
        # Pattern: "January 15" or "15th January" etc.
        day_patterns = re.findall(r'\b(\d{1,2})(?:st|nd|rd|th)?\b', text)
        for d in day_patterns:
            day = int(d)
            if 1 <= day <= 31:
                days.add(day)
        
        return list(days)
    
    @classmethod
    def extract_amounts(cls, text: str) -> List[float]:
        """Extract monetary amounts from text"""
        amounts = []
        
        # Pattern: $1,234.56 or $1234.56 or $1234 or 1,234.56 USD etc.
        patterns = [
            r'\$\s*([\d,]+\.?\d*)',  # $1,234.56
            r'([\d,]+\.\d{2})\s*(?:USD|usd|dollars?)',  # 1234.56 USD
            r'(?:USD|usd|\$)\s*([\d,]+\.?\d*)',  # USD 1234
            r'₹\s*([\d,]+\.?\d*)',  # Indian Rupee
            r'€\s*([\d,]+\.?\d*)',  # Euro
            r'£\s*([\d,]+\.?\d*)',  # Pound
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    amount = float(match.replace(',', ''))
                    if amount > 0:
                        amounts.append(amount)
                except ValueError:
                    continue
        
        return list(set(amounts))
    
    @classmethod
    def extract_categories(cls, text: str) -> List[str]:
        """Extract financial categories based on keywords"""
        categories = set()
        text_lower = text.lower()
        
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    categories.add(category)
                    break
        
        return list(categories)
    
    @classmethod
    def extract_all(cls, text: str) -> Dict:
        """Extract all metadata from text"""
        return {
            'content_years': cls.extract_years(text),
            'content_months': cls.extract_months(text),
            'content_days': cls.extract_days(text),
            'content_amounts': cls.extract_amounts(text),
            'content_categories': cls.extract_categories(text),
            'amount_min': min(cls.extract_amounts(text)) if cls.extract_amounts(text) else None,
            'amount_max': max(cls.extract_amounts(text)) if cls.extract_amounts(text) else None,
        }


class RAGMetrics:
    """Class to compute and display RAG retrieval metrics"""
    
    def __init__(self, relevance_threshold: float = 0.3, use_percentile: bool = True, percentile: float = 50):
        self.relevance_threshold = relevance_threshold
        self.use_percentile = use_percentile  # Use percentile-based relevance
        self.percentile = percentile  # Documents above this percentile are "relevant"
        self.query_history: List[Dict] = []
    
    def sigmoid(self, x: np.ndarray) -> np.ndarray:
        """Apply sigmoid to convert logits to probabilities"""
        # Clip to avoid overflow
        x = np.clip(x, -500, 500)
        return 1 / (1 + np.exp(-x))
    
    def compute_metrics(self, scores: np.ndarray, k: int) -> Dict[str, float]:
        """
        Compute Precision@k and Recall@k using re-ranker scores.
        Uses either absolute threshold or percentile-based relevance.
        """
        # Normalize scores using sigmoid (convert logits to probabilities)
        normalized_scores = self.sigmoid(scores)
        
        # Determine relevance threshold
        if self.use_percentile:
            # Use percentile-based threshold (adaptive to score distribution)
            dynamic_threshold = np.percentile(normalized_scores, self.percentile)
            threshold = dynamic_threshold
        else:
            threshold = self.relevance_threshold
        
        # Determine relevant documents based on threshold
        relevant_mask = normalized_scores > threshold
        total_relevant = np.sum(relevant_mask)
        
        # Get top-k indices (scores are already sorted descending)
        top_k_relevant = np.sum(normalized_scores[:k] > threshold)
        
        # Precision@k: relevant docs in top-k / k
        precision_at_k = top_k_relevant / k if k > 0 else 0.0
        
        # Recall@k: relevant docs in top-k / total relevant docs
        recall_at_k = top_k_relevant / total_relevant if total_relevant > 0 else 0.0
        
        # Mean Reciprocal Rank (MRR)
        mrr = 0.0
        for i, score in enumerate(normalized_scores):
            if score > threshold:
                mrr = 1.0 / (i + 1)
                break
        
        # Average Precision
        precisions = []
        relevant_count = 0
        for i, score in enumerate(normalized_scores[:k]):
            if score > threshold:
                relevant_count += 1
                precisions.append(relevant_count / (i + 1))
        avg_precision = np.mean(precisions) if precisions else 0.0
        
        # Normalized Discounted Cumulative Gain (NDCG@k)
        dcg = 0.0
        for i, score in enumerate(normalized_scores[:k]):
            rel = 1 if score > threshold else 0
            dcg += rel / np.log2(i + 2)  # i+2 because log2(1) = 0
        
        # Ideal DCG (all relevant docs at top)
        ideal_rels = sorted([1 if s > threshold else 0 for s in normalized_scores], reverse=True)
        idcg = sum(rel / np.log2(i + 2) for i, rel in enumerate(ideal_rels[:k]))
        ndcg = dcg / idcg if idcg > 0 else 0.0
        
        return {
            "precision_at_k": precision_at_k,
            "recall_at_k": recall_at_k,
            "mrr": mrr,
            "avg_precision": avg_precision,
            "ndcg_at_k": ndcg,
            "total_relevant": int(total_relevant),
            "relevant_in_top_k": int(top_k_relevant),
            "threshold_used": threshold,
            "normalized_scores": normalized_scores.tolist()
        }
    
    def display_metrics(self, metrics: Dict[str, float], k: int, query: str):
        """Display metrics in terminal with formatting"""
        print("\n" + "="*60)
        print("📊 RAG RETRIEVAL METRICS")
        print("="*60)
        print(f"Query: {query[:50]}..." if len(query) > 50 else f"Query: {query}")
        print("-"*60)
        print(f"  Precision@{k}:     {metrics['precision_at_k']:.4f}  ({metrics['relevant_in_top_k']}/{k} relevant in top-{k})")
        print(f"  Recall@{k}:        {metrics['recall_at_k']:.4f}  ({metrics['relevant_in_top_k']}/{metrics['total_relevant']} relevant retrieved)")
        print(f"  NDCG@{k}:          {metrics['ndcg_at_k']:.4f}")
        print(f"  MRR:              {metrics['mrr']:.4f}")
        print(f"  Avg Precision:    {metrics['avg_precision']:.4f}")
        print("-"*60)
        threshold_type = "Percentile-based" if self.use_percentile else "Fixed"
        print(f"  Threshold Type: {threshold_type}")
        print(f"  Threshold Used: {metrics['threshold_used']:.6f}")
        print("="*60 + "\n")
    
    def log_query(self, query: str, metrics: Dict[str, float]):
        """Log query metrics for aggregate statistics"""
        self.query_history.append({
            "query": query,
            "metrics": metrics
        })
    
    def display_aggregate_stats(self):
        """Display aggregate statistics across all queries"""
        if not self.query_history:
            print("No queries logged yet.")
            return

        avg_precision = np.mean([q["metrics"]["precision_at_k"] for q in self.query_history])
        avg_recall = np.mean([q["metrics"]["recall_at_k"] for q in self.query_history])
        avg_mrr = np.mean([q["metrics"]["mrr"] for q in self.query_history])
        avg_ndcg = np.mean([q["metrics"]["ndcg_at_k"] for q in self.query_history])
        
        print("\n" + "="*60)
        print("📈 AGGREGATE RAG METRICS (All Queries)")
        print("="*60)
        print(f"  Total Queries:      {len(self.query_history)}")
        print(f"  Avg Precision@k:    {avg_precision:.4f}")
        print(f"  Avg Recall@k:       {avg_recall:.4f}")
        print(f"  Avg NDCG@k:         {avg_ndcg:.4f}")
        print(f"  Avg MRR:            {avg_mrr:.4f}")
        print("="*60 + "\n")

class RAGService:
    def __init__(self):
        self.embeddings = None
        self.vector_store = None
        self.text_splitter = None
        self.openai_client = None
        self.reranker = None
        # Use percentile-based relevance: docs above 50th percentile are "relevant"
        self.metrics = RAGMetrics(use_percentile=True, percentile=50)
        self.vector_store_path = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
        
    async def initialize(self):
        """Initialize the RAG service components"""
        try:
            # Initialize embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            
            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            
            # Initialize OpenAI client
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            print("Initialized OpenAI client")
            
            # Initialize cross-encoder reranker
            self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)
            print("Initialized cross-encoder reranker")
            
            # Load existing vector store if available
            await self._load_vector_store()
            
        except Exception as e:
            print(f"Error initializing RAG service: {e}")
            raise e
    
    async def _load_vector_store(self):
        """Load existing vector store or create new one"""
        try:
            if os.path.exists(self.vector_store_path):
                self.vector_store = FAISS.load_local(
                    self.vector_store_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print("Loaded existing vector store")
            else:
                # Create empty vector store
                sample_doc = Document(page_content="Sample initialization document", metadata={})
                self.vector_store = FAISS.from_documents([sample_doc], self.embeddings)
                print("Created new vector store")
        except Exception as e:
            print(f"Error loading vector store: {e}")
            # Create empty vector store as fallback
            sample_doc = Document(page_content="Sample initialization document", metadata={})
            self.vector_store = FAISS.from_documents([sample_doc], self.embeddings)
    
    async def process_documents(self, file_paths: List[str]):
        """Process PDF documents and add to vector store"""
        try:
            all_documents = []
            upload_timestamp = datetime.now().isoformat()
            
            for file_path in file_paths:
                # Load PDF
                loader = PyPDFLoader(file_path)
                documents = loader.load()
                
                # Split documents
                chunks = self.text_splitter.split_documents(documents)
                
                # Extract file info for metadata
                file_name = os.path.basename(file_path)
                file_extension = os.path.splitext(file_name)[1].lower()
                file_size = os.path.getsize(file_path)
                
                # Add rich metadata to each chunk
                for i, chunk in enumerate(chunks):
                    # Extract content-based metadata (years, months, amounts, categories)
                    content_metadata = ContentMetadataExtractor.extract_all(chunk.page_content)
                    
                    chunk.metadata.update({
                        "source_file": file_name,
                        "file_path": file_path,
                        "file_type": file_extension,
                        "file_size_bytes": file_size,
                        "upload_date": upload_timestamp,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "page_number": chunk.metadata.get("page", 0) + 1,  # 1-indexed
                        # Content-based metadata
                        "content_years": content_metadata['content_years'],
                        "content_months": content_metadata['content_months'],
                        "content_days": content_metadata['content_days'],
                        "content_amounts": content_metadata['content_amounts'],
                        "content_categories": content_metadata['content_categories'],
                        "amount_min": content_metadata['amount_min'],
                        "amount_max": content_metadata['amount_max'],
                    })
                
                all_documents.extend(chunks)
            
            if all_documents:
                # Add to vector store
                if self.vector_store.index.ntotal == 1:  # Only sample doc exists
                    self.vector_store = FAISS.from_documents(all_documents, self.embeddings)
                else:
                    self.vector_store.add_documents(all_documents)
                
                # Save vector store
                os.makedirs(os.path.dirname(self.vector_store_path), exist_ok=True)
                self.vector_store.save_local(self.vector_store_path)
                
                # Display upload metrics
                print("\n" + "="*60)
                print("📁 DOCUMENT UPLOAD METRICS")
                print("="*60)
                print(f"  Files Processed:    {len(file_paths)}")
                print(f"  Total Chunks:       {len(all_documents)}")
                print(f"  Vector Store Size:  {self.vector_store.index.ntotal} vectors")
                print(f"  Chunk Size:         {self.text_splitter._chunk_size} chars")
                print(f"  Chunk Overlap:      {self.text_splitter._chunk_overlap} chars")
                print("="*60 + "\n")
            
        except Exception as e:
            print(f"Error processing documents: {e}")
            raise e
    
    def _apply_metadata_filters(self, documents: List[Document], filters: Optional[Dict] = None) -> List[Document]:
        """
        Apply metadata filters to a list of documents.
        
        Content-based filters (extracted from document text):
        - year: int or List[int] - filter by year(s) mentioned in content (e.g., 2024)
        - month: int or List[int] - filter by month(s) mentioned in content (1-12)
        - day: int or List[int] - filter by day(s) mentioned in content (1-31)
        - category: str or List[str] - filter by financial category (travel, food, utilities, etc.)
        - amount_min: float - filter chunks with amounts >= this value
        - amount_max: float - filter chunks with amounts <= this value
        
        File-based filters:
        - source_file: str or List[str] - filter by file name(s)
        - page_number: int or List[int] - filter by page number(s)
        """
        if not filters:
            return documents
        
        filtered_docs = []
        
        for doc in documents:
            metadata = doc.metadata
            include = True
            
            # ===== CONTENT-BASED FILTERS =====
            
            # Filter by year (content)
            if include and "year" in filters:
                allowed_years = filters["year"]
                if isinstance(allowed_years, int):
                    allowed_years = [allowed_years]
                doc_years = metadata.get("content_years", [])
                # Check if any allowed year is in the document's years
                if not any(y in doc_years for y in allowed_years):
                    include = False
            
            # Filter by month (content)
            if include and "month" in filters:
                allowed_months = filters["month"]
                if isinstance(allowed_months, int):
                    allowed_months = [allowed_months]
                doc_months = metadata.get("content_months", [])
                if not any(m in doc_months for m in allowed_months):
                    include = False
            
            # Filter by day (content)
            if include and "day" in filters:
                allowed_days = filters["day"]
                if isinstance(allowed_days, int):
                    allowed_days = [allowed_days]
                doc_days = metadata.get("content_days", [])
                if not any(d in doc_days for d in allowed_days):
                    include = False
            
            # Filter by category (content)
            if include and "category" in filters:
                allowed_categories = filters["category"]
                if isinstance(allowed_categories, str):
                    allowed_categories = [allowed_categories.lower()]
                else:
                    allowed_categories = [c.lower() for c in allowed_categories]
                doc_categories = metadata.get("content_categories", [])
                if not any(c in doc_categories for c in allowed_categories):
                    include = False
            
            # Filter by amount range (content)
            if include and "amount_min" in filters:
                doc_amounts = metadata.get("content_amounts", [])
                if not doc_amounts or max(doc_amounts) < filters["amount_min"]:
                    include = False
            
            if include and "amount_max" in filters:
                doc_amounts = metadata.get("content_amounts", [])
                if not doc_amounts or min(doc_amounts) > filters["amount_max"]:
                    include = False
            
            # ===== FILE-BASED FILTERS =====
            
            # Filter by source file
            if include and "source_file" in filters:
                allowed_files = filters["source_file"]
                if isinstance(allowed_files, str):
                    allowed_files = [allowed_files]
                if metadata.get("source_file") not in allowed_files:
                    include = False
            
            # Filter by page number
            if include and "page_number" in filters:
                allowed_pages = filters["page_number"]
                if isinstance(allowed_pages, int):
                    allowed_pages = [allowed_pages]
                if metadata.get("page_number") not in allowed_pages:
                    include = False
            
            if include:
                filtered_docs.append(doc)
        
        return filtered_docs
    
    async def query(self, query: str, k: int = 5, filters: Optional[Dict] = None) -> str:
        """Query the RAG system with re-ranking and optional metadata filtering"""
        try:
            # Input guardrails - validate the query (NeMo async)
            is_allowed, validation_msg, validation_details = await guardrails_service.validate_input(query)
            
            if not is_allowed:
                print(f"⛔ Query blocked by guardrails: {validation_msg}")
                return f"I cannot process this request. {validation_msg}"
            
            # Use sanitized query if PII was detected
            sanitized_query = validation_details.get("sanitized_query", query)
            if sanitized_query != query:
                print(f"🔒 PII detected and masked in query")
            
            # Log any warnings
            if validation_details.get("warnings"):
                print(f"⚠️ Guardrail warnings: {validation_details['warnings']}")
            
            if not self.vector_store or self.vector_store.index.ntotal <= 1:
                return "No documents have been uploaded yet. Please upload some PDF documents first."
            
            # If filters are applied, retrieve more candidates to account for filtering
            filter_multiplier = 5 if filters else 3
            initial_k = min(k * filter_multiplier, self.vector_store.index.ntotal)
            candidate_docs = self.vector_store.similarity_search(sanitized_query, k=initial_k)
            
            # Apply metadata filters if provided
            if filters:
                print(f"\n🔍 Applying metadata filters: {filters}")
                pre_filter_count = len(candidate_docs)
                candidate_docs = self._apply_metadata_filters(candidate_docs, filters)
                print(f"   Filtered: {pre_filter_count} → {len(candidate_docs)} documents")
                
                if len(candidate_docs) == 0:
                    return "No documents match the specified filters. Please adjust your filter criteria."
            
            # Re-rank using cross-encoder
            if self.reranker and len(candidate_docs) > 0:
                # Prepare query-document pairs for scoring
                pairs = [[query, doc.page_content] for doc in candidate_docs]
                
                # Get re-ranking scores
                scores = self.reranker.predict(pairs)
                
                # Sort documents by re-ranking score (descending)
                doc_scores = list(zip(candidate_docs, scores))
                doc_scores.sort(key=lambda x: x[1], reverse=True)
                
                # Get sorted scores for metrics
                sorted_scores = np.array([score for _, score in doc_scores])
                
                # Compute and display metrics
                metrics = self.metrics.compute_metrics(sorted_scores, k)
                self.metrics.display_metrics(metrics, k, query)
                self.metrics.log_query(query, metrics)
                
                # Get normalized scores for display
                normalized_scores = metrics['normalized_scores']

                # Rescale confidence to a meaningful 0-1 range using the max raw logit.
                # Cross-encoder logits typically range -10 (no match) to +10 (strong match).
                # Linear map: logit -10 → 0.0, logit 0 → 0.5, logit +10 → 1.0
                top_logit = float(sorted_scores[0])
                confidence_score = max(0.0, min(1.0, (top_logit + 10.0) / 20.0))

                # Display score distribution
                print("📊 Re-ranker Score Distribution:")
                print(f"   Raw Scores (logits): Max={sorted_scores[0]:.4f} | Min={sorted_scores[-1]:.4f} | Mean={np.mean(sorted_scores):.4f}")
                print(f"   Normalized (sigmoid): Max={normalized_scores[0]:.4f} | Min={normalized_scores[-1]:.4f}")
                print(f"   Rescaled Confidence : {confidence_score:.4f}  ({confidence_score*100:.1f}%)")
                print(f"   Top-{k} Raw Logits  : {[f'{s:.2f}' for s in sorted_scores[:k]]}")
                print("-"*60 + "\n")

                # Take top-k after re-ranking
                relevant_docs = [doc for doc, score in doc_scores[:k]]
            else:
                relevant_docs = candidate_docs[:k]
                confidence_score = 0.5  # Default confidence when no re-ranker
            
            # Prepare context
            context = "\n\n".join([
                f"Source: {doc.metadata.get('source_file', 'Unknown')}\n{doc.page_content}"
                for doc in relevant_docs
            ])
            
            # Generate prompt
            prompt = f"""
You are a financial expert assistant. Based on the following financial documents, please answer the user's question accurately and comprehensively.

Context from financial documents:
{context}

User Question: {query}

Please provide a detailed, accurate answer based on the provided financial documents. If the information is not available in the documents, please state that clearly.

Answer:"""
            
            # Generate response using OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a financial expert assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            raw_response = response.choices[0].message.content
            
            # Output guardrails - validate and enhance the response (NeMo async)
            processed_response, output_details = await guardrails_service.validate_output(
                response=raw_response,
                query=query,
                context=context,
                confidence_score=confidence_score
            )

            # Log NeMo output guardrail results
            print(f"🛡️ [NeMo] Output Guardrails Applied:")
            print(f"   Grounding : {output_details.get('grounding', {}).get('is_grounded', 'N/A')}")
            print(f"   PII Leak  : {output_details.get('pii_leakage', {}).get('detected', [])}")
            print(f"   Disclaimer: {output_details.get('disclaimer', {}).get('action', 'N/A')}")
            print(f"   Confidence: {confidence_score:.3f}")
            
            return processed_response
            
        except Exception as e:
            print(f"Error querying RAG system: {e}")
            return f"Error processing your query: {str(e)}"
    
    async def get_document_count(self) -> int:
        """Get the number of documents in the vector store"""
        if self.vector_store:
            return self.vector_store.index.ntotal
        return 0
    
    def get_aggregate_metrics(self):
        """Display aggregate metrics across all queries"""
        self.metrics.display_aggregate_stats()
    
    def set_relevance_threshold(self, threshold: float):
        """Set the relevance threshold for metrics calculation (disables percentile mode)"""
        self.metrics.use_percentile = False
        self.metrics.relevance_threshold = threshold
        print(f"Relevance threshold set to: {threshold} (fixed mode)")
    
    def set_percentile_mode(self, percentile: float = 50):
        """Use percentile-based relevance determination"""
        self.metrics.use_percentile = True
        self.metrics.percentile = percentile
        print(f"Percentile mode enabled: documents above {percentile}th percentile are relevant")
    
    async def get_available_documents(self) -> Dict:
        """Get list of all unique documents and their metadata for filtering"""
        if not self.vector_store or self.vector_store.index.ntotal <= 1:
            return {
                "documents": [], 
                "file_types": [], 
                "available_years": [],
                "available_months": [],
                "available_categories": [],
                "amount_range": {"min": None, "max": None},
                "total_chunks": 0
            }
        
        # Retrieve all documents to extract unique metadata
        all_docs = self.vector_store.similarity_search("", k=self.vector_store.index.ntotal)
        
        documents = {}
        file_types = set()
        all_years = set()
        all_months = set()
        all_categories = set()
        all_amounts = []
        
        for doc in all_docs:
            source_file = doc.metadata.get("source_file", "Unknown")
            file_type = doc.metadata.get("file_type", "")
            
            if source_file not in documents:
                documents[source_file] = {
                    "source_file": source_file,
                    "file_type": file_type,
                    "upload_date": doc.metadata.get("upload_date", ""),
                    "total_chunks": doc.metadata.get("total_chunks", 0),
                    "file_size_bytes": doc.metadata.get("file_size_bytes", 0),
                    "pages": set(),
                    "years": set(),
                    "months": set(),
                    "categories": set()
                }
            
            # Track pages
            page = doc.metadata.get("page_number", 0)
            if page:
                documents[source_file]["pages"].add(page)
            
            # Track content metadata
            doc_years = doc.metadata.get("content_years", [])
            doc_months = doc.metadata.get("content_months", [])
            doc_categories = doc.metadata.get("content_categories", [])
            doc_amounts = doc.metadata.get("content_amounts", [])
            
            all_years.update(doc_years)
            all_months.update(doc_months)
            all_categories.update(doc_categories)
            all_amounts.extend(doc_amounts)
            
            documents[source_file]["years"].update(doc_years)
            documents[source_file]["months"].update(doc_months)
            documents[source_file]["categories"].update(doc_categories)
            
            if file_type:
                file_types.add(file_type)
        
        # Convert sets to sorted lists
        for doc_info in documents.values():
            doc_info["pages"] = sorted(list(doc_info["pages"]))
            doc_info["years"] = sorted(list(doc_info["years"]))
            doc_info["months"] = sorted(list(doc_info["months"]))
            doc_info["categories"] = sorted(list(doc_info["categories"]))
        
        return {
            "documents": list(documents.values()),
            "file_types": sorted(list(file_types)),
            "available_years": sorted(list(all_years)),
            "available_months": sorted(list(all_months)),
            "available_categories": sorted(list(all_categories)),
            "amount_range": {
                "min": min(all_amounts) if all_amounts else None,
                "max": max(all_amounts) if all_amounts else None
            },
            "total_chunks": self.vector_store.index.ntotal
        }
