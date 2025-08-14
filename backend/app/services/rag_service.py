import os
import asyncio
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class RAGService:
    def __init__(self):
        self.embeddings = None
        self.vector_store = None
        self.text_splitter = None
        self.gemini_model = None
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
            
            # Initialize Gemini
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
            
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
            
            for file_path in file_paths:
                # Load PDF
                loader = PyPDFLoader(file_path)
                documents = loader.load()
                
                # Split documents
                chunks = self.text_splitter.split_documents(documents)
                
                # Add metadata
                for chunk in chunks:
                    chunk.metadata.update({
                        "source_file": os.path.basename(file_path),
                        "file_path": file_path
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
                
                print(f"Processed {len(all_documents)} document chunks")
            
        except Exception as e:
            print(f"Error processing documents: {e}")
            raise e
    
    async def query(self, query: str, k: int = 5) -> str:
        """Query the RAG system"""
        try:
            if not self.vector_store or self.vector_store.index.ntotal <= 1:
                return "No documents have been uploaded yet. Please upload some PDF documents first."
            
            # Retrieve relevant documents
            relevant_docs = self.vector_store.similarity_search(query, k=k)
            
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
            
            # Generate response using Gemini
            response = self.gemini_model.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            print(f"Error querying RAG system: {e}")
            return f"Error processing your query: {str(e)}"
    
    async def get_document_count(self) -> int:
        """Get the number of documents in the vector store"""
        if self.vector_store:
            return self.vector_store.index.ntotal
        return 0
