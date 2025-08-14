# Project Requirements Specification  
**Project Title:** IntelliFinance – AI-Powered Financial Insights and Decision Support System  

---

## 1. Introduction  
This project aims to build an advanced AI-powered financial assistant that can:  
- Analyze financial reports  
- Assist in making trade decisions  
- Generate personalized savings/investment plan flowcharts  
- Provide financial news updates  
- Summarize financial data efficiently  

The system will integrate:  
- **RAG (Retrieval-Augmented Generation)** for document-based queries  
- **Agentic workflows** for trade decision-making  
- **Multi-service conversational UI** for user interaction  

---

## 2. Objectives  
- Enable **context-aware querying** of multiple uploaded financial reports using RAG, persistent FAISS storage, and Hugging Face embeddings.  
- Automate **trade decision-making workflows** using CrewAI agents with memory and OpenAI APIs.  
- Generate **workflow diagrams** for financial planning using React Flow and LLaMA models via Groq API.  
- Deliver **summarized trade decisions** using IBM Granite 2B Instruct model via Ollama.  
- Present **real-time financial news updates** for researched companies.  
- Provide a **multi-threaded chat UI** with service-specific channels.  

---

## 3. Scope of Work  

### RAG-Based Financial Report Querying  
- Accept multiple PDF uploads  
- Parse and chunk documents using **LangChain RecursiveCharacterTextSplitter**  
- Generate embeddings via **Hugging Face models**  
- Store vectors persistently using **FAISS**  
- Retrieve relevant chunks for context-aware answers via **Gemini 1.5 Flash**  

### Trade Decision Workflow (Agentic)  
- **CrewAI** orchestrates trade decision agents  
- **Research Agent** (Serper API) fetches trending company data  
- **Analysis Agent** (OpenAI API) performs sentiment and market analysis  
- **Decision Agent** (OpenAI API + Memory) produces buy/sell/hold recommendations  
- Decision summary stored in agent memory  
- Summary passed to **IBM Granite 2B Instruct** (via Ollama) for short notes  

### Workflow Diagram Generation  
- User requests yearly savings/investment plans  
- **Groq API (LLaMA model)** generates plan outline  
- **React Flow** renders workflow visually  

### Finance News Feed  
- Aggregate and display relevant news for researched companies  

---

## 4. User Interface Requirements  
The application’s **main chat interface** will serve as the central space for answering general finance-related queries.  
A **sidebar** will provide quick access to four specialized service channels, each functioning as an independent conversational thread:  

1. **Trade Decision Assistant** – AI-driven buy/sell/hold recommendations based on market research  
2. **Financial Flowchart Generator** – AI-powered yearly savings/investment plan workflows  
3. **Finance News Feed** – Latest market updates and company-specific news  
4. **RAG-Based Financial Summaries** – Multi-report upload and context-aware AI summaries  

---

## 5. Technology Stack  

**Frontend:**  
- React.js  
- Tailwind CSS  
- React Flow  

**Backend:**  
- FastAPI  

**LLM APIs:**  
- Gemini 1.5 Flash (financial query answering)  
- Hugging Face (embeddings)  
- OpenAI API (analysis, decision-making)  
- IBM Granite 2B Instruct via Ollama (short notes)  
- Groq API (flowchart generation with LLaMA)  

**Agents & Orchestration:**  
- CrewAI Framework with Memory  

**Search & Retrieval:**  
- LangChain  
- Persistent FAISS Vector Store  

**Research Tool:**  
- Serper API  

**Document Parsing:**  
- LangChain PDF Loaders  

---

## 6. Novelty / Uniqueness  
- Multi-service conversational finance assistant with **distinct chat threads** for specialized tasks  
- **Persistent multi-PDF RAG** enabling long-term, context-aware financial analysis  
- Integrated agentic decision-making with **market research, sentiment analysis, and real-time news aggregation**  
- Cross-model workflow combining **OpenAI, Gemini, Hugging Face, LLaMA, and IBM Granite** in one cohesive system  

---

## 7. Business / Social Impact  
- Democratizes access to AI-powered financial analysis for individuals and small businesses  
- Assists in **informed decision-making** in stock trading and investments  
- Enhances **financial literacy** through AI-generated insights and summaries  
- Saves time by **automating data parsing, analysis, and visualization**  

---

## 8. Expected Deliverables  
- Fully functional web application with chat and sidebar service channels  
- Persistent multi-PDF RAG pipeline with FAISS storage  
- Trade decision-making AI agent workflow  
- Financial planning flowchart generator  
- News aggregation system for researched companies  
- Short-note generator using IBM Granite 2B Instruct  

---

## 9. Expected Solutions from Provided Photo  
(Includes the original “expected solutions” from the project brief)  
- Finance report RAG implementation with FAISS and Gemini 1.5 Flash  
- Financial flowchart generation using React Flow and Groq API  
- Trade decision agent workflow using CrewAI and OpenAI API  
- Short-note summary feature using IBM Granite via Ollama  
- Company news feed integration  

---
