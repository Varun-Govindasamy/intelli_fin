from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from typing import List, Optional
import uvicorn
from contextlib import asynccontextmanager

from app.services.rag_service import RAGService
from app.services.trade_agent_service import TradeAgentService
from app.services.flowchart_service import FlowchartService
from app.services.news_service import NewsService
from app.services.chat_service import ChatService
from app.services.guardrails_service import guardrails_service
from app.utils.file_manager import FileManager

# Load environment variables
load_dotenv()

# Initialize services
rag_service = None
trade_agent_service = None
flowchart_service = None
news_service = None
chat_service = None
file_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_service, trade_agent_service, flowchart_service, news_service, chat_service, file_manager

    file_manager = FileManager()

    try:
        rag_service = RAGService()
        await rag_service.initialize()
        print("✅ RAG service initialized")
    except Exception as e:
        print(f"⚠️  RAG service failed to initialize: {e}")

    try:
        trade_agent_service = TradeAgentService()
        print("✅ Trade agent service initialized")
    except Exception as e:
        print(f"⚠️  Trade agent service failed to initialize: {e}")

    try:
        flowchart_service = FlowchartService()
        print("✅ Flowchart service initialized")
    except Exception as e:
        print(f"⚠️  Flowchart service failed to initialize: {e}")

    try:
        news_service = NewsService()
        print("✅ News service initialized")
    except Exception as e:
        print(f"⚠️  News service failed to initialize: {e}")

    try:
        chat_service = ChatService()
        print("✅ Chat service initialized")
    except Exception as e:
        print(f"⚠️  Chat service failed to initialize: {e}")

    yield

    # Shutdown
    pass

# Create FastAPI app
app = FastAPI(
    title="IntelliFinance API",
    description="AI-Powered Financial Insights and Decision Support System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS — origins are read from env so Railway can allow the Vercel frontend
# Set CORS_ORIGINS on Railway to your Vercel URL (comma-separated for multiple)
# If not set, defaults to allow all origins (safe for public APIs)
_cors_origins_raw = os.getenv("CORS_ORIGINS", "*")
if _cors_origins_raw.strip() == "*":
    _cors_origins = ["*"]
else:
    _cors_origins = [o.strip() for o in _cors_origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=False if "*" in _cors_origins else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "IntelliFinance API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# RAG Service Endpoints
@app.post("/api/rag/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload PDF documents for RAG processing"""
    try:
        uploaded_files = []
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"Only PDF files are allowed. Got: {file.filename}")
            
            file_path = await file_manager.save_upload(file)
            uploaded_files.append(file_path)
        
        # Process documents through RAG service
        await rag_service.process_documents(uploaded_files)
        
        return {"message": f"Successfully uploaded and processed {len(uploaded_files)} documents"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rag/query")
async def query_documents(
    query: str = Form(...),
    # Content-based filters (extracted from document text)
    year: Optional[str] = Form(default=None),          # Comma-separated years (e.g., "2024,2023")
    month: Optional[str] = Form(default=None),         # Comma-separated months 1-12 (e.g., "1,2,3")
    day: Optional[str] = Form(default=None),           # Comma-separated days 1-31 (e.g., "15,16")
    category: Optional[str] = Form(default=None),      # Comma-separated categories (e.g., "travel,food")
    amount_min: Optional[float] = Form(default=None),  # Minimum amount filter
    amount_max: Optional[float] = Form(default=None),  # Maximum amount filter
    # File-based filters
    source_files: Optional[str] = Form(default=None),  # Comma-separated file names
    page_numbers: Optional[str] = Form(default=None),  # Comma-separated page numbers
):
    """
    Query the RAG system with a financial question and optional metadata filters.
    
    Content filters: year, month, day, category, amount_min, amount_max
    File filters: source_files, page_numbers
    
    Categories: travel, food, utilities, salary, rent, insurance, healthcare, 
                entertainment, shopping, investment, tax, education, miscellaneous
    """
    try:
        # Build filters dict from form parameters
        filters = {}
        
        # Content-based filters
        if year:
            filters["year"] = [int(y.strip()) for y in year.split(",") if y.strip()]
        
        if month:
            filters["month"] = [int(m.strip()) for m in month.split(",") if m.strip()]
        
        if day:
            filters["day"] = [int(d.strip()) for d in day.split(",") if d.strip()]
        
        if category:
            filters["category"] = [c.strip().lower() for c in category.split(",") if c.strip()]
        
        if amount_min is not None:
            filters["amount_min"] = amount_min
        
        if amount_max is not None:
            filters["amount_max"] = amount_max
        
        # File-based filters
        if source_files:
            filters["source_file"] = [f.strip() for f in source_files.split(",") if f.strip()]
        
        if page_numbers:
            filters["page_number"] = [int(p.strip()) for p in page_numbers.split(",") if p.strip()]
        
        # Pass filters only if any were provided
        response = await rag_service.query(query, filters=filters if filters else None)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rag/documents")
async def get_available_documents():
    """Get list of all uploaded documents and their metadata for filtering"""
    try:
        documents_info = await rag_service.get_available_documents()
        return documents_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Trade Decision Endpoints
@app.post("/api/trade/analyze")
async def analyze_trade(
    company_symbol: str = Form(...),
    analysis_type: str = Form(default="comprehensive")
):
    """Get trade decision analysis for a company"""
    try:
        result = await trade_agent_service.analyze_trade_decision(company_symbol, analysis_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trade/history")
async def get_trade_history():
    """Get trade decision history"""
    try:
        history = await trade_agent_service.get_decision_history()
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trade/comprehensive-analysis")
async def comprehensive_trade_analysis(
    budget: float = Form(...),
    risk_level: str = Form(...),  # 'low', 'medium', 'high'
    time_horizon: str = Form(...),  # 'short', 'medium', 'long'
    sector_preferences: str = Form(default=""),  # Comma-separated
    symbols: str = Form(...)  # Comma-separated stock symbols
):
    """Get comprehensive trade analysis with position sizing"""
    try:
        # Import the UserProfile class locally to avoid issues
        from app.services.trade_agent_service import UserProfile
        
        # Parse inputs
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        preference_list = [s.strip() for s in sector_preferences.split(",") if s.strip()]
        
        # Create user profile
        user_profile = UserProfile(
            budget=budget,
            risk_level=risk_level.lower(),
            time_horizon=time_horizon.lower(),
            sector_preferences=preference_list
        )
        
        # Run comprehensive analysis
        result = await trade_agent_service.comprehensive_trade_analysis(symbol_list, user_profile)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Flowchart Generation Endpoints
@app.post("/api/flowchart/generate")
async def generate_flowchart(
    financial_goal: str = Form(...),
    time_horizon: str = Form(default="1 year"),
    risk_tolerance: str = Form(default="moderate")
):
    """Generate financial planning flowchart"""
    try:
        flowchart_data = await flowchart_service.generate_flowchart(
            financial_goal, time_horizon, risk_tolerance
        )
        return flowchart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# News Service Endpoints
@app.get("/api/news/companies")
async def get_company_news(symbols: str):
    """Get news for specified company symbols (comma-separated)"""
    try:
        symbol_list = [s.strip() for s in symbols.split(',')]
        news = await news_service.get_company_news(symbol_list)
        return {"news": news}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/general")
async def get_general_financial_news():
    """Get general financial news"""
    try:
        news = await news_service.get_general_financial_news()
        return {"news": news}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# General Chat Endpoints
@app.post("/api/chat/general")
async def general_chat(message: str = Form(...)):
    """General financial chat using Gemini"""
    try:
        response = await chat_service.general_chat(message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/summary")
async def generate_summary(content: str = Form(...)):
    """Generate short summary using IBM Granite via Ollama"""
    try:
        summary = await chat_service.generate_summary(content)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Guardrails Endpoints
@app.post("/api/guardrails/validate-input")
async def validate_input(query: str = Form(...)):
    """Validate user input against guardrails (injection, PII, topic relevance)"""
    try:
        is_allowed, message, details = await guardrails_service.validate_input(query)
        return {
            "allowed": is_allowed,
            "message": message,
            "details": details
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/guardrails/validate-output")
async def validate_output(
    response: str = Form(...),
    query: str = Form(...),
    context: Optional[str] = Form(default=""),
    confidence_score: Optional[float] = Form(default=1.0)
):
    """Validate and process AI output (grounding, disclaimers, warnings)"""
    try:
        processed_response, details = await guardrails_service.validate_output(
            response=response,
            query=query,
            context=context,
            confidence_score=confidence_score
        )
        return {
            "processed_response": processed_response,
            "details": details
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/guardrails/status")
async def get_guardrails_status():
    """Get current guardrails configuration status"""
    return {
        "enabled": guardrails_service.enabled,
        "strict_mode": guardrails_service.strict_mode,
        "provider": "NVIDIA NeMo Guardrails",
        "input_checks": [
            "domain_control", "jailbreak_injection", "pii_masking",
            "regulatory_compliance", "sensitive_query_flagging"
        ],
        "output_checks": [
            "hallucination_grounding", "disclaimer_injection", "pii_leakage",
            "numerical_sanity", "sentiment_toxicity", "source_citation"
        ]
    }

@app.post("/api/guardrails/configure")
async def configure_guardrails(
    enabled: Optional[bool] = Form(default=None),
    strict_mode: Optional[bool] = Form(default=None)
):
    """Configure guardrails settings"""
    try:
        if enabled is not None:
            guardrails_service.set_enabled(enabled)
        if strict_mode is not None:
            guardrails_service.set_strict_mode(strict_mode)
        
        return {
            "enabled": guardrails_service.enabled,
            "strict_mode": guardrails_service.strict_mode,
            "message": "Guardrails configuration updated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("FASTAPI_HOST", "localhost"),
        port=int(os.getenv("FASTAPI_PORT", 8000)),
        reload=True
    )
