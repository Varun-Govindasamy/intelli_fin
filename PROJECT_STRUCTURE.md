# IntelliFinance Project Structure

```
finance-bot/
├── README.md                          # Main project documentation
├── project_requirements.md            # Original requirements specification
│
├── backend/                           # FastAPI Backend
│   ├── setup.bat                      # Windows setup script
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # Environment variables template
│   ├── main.py                        # FastAPI application entry point
│   │
│   ├── app/                           # Application package
│   │   ├── __init__.py
│   │   ├── services/                  # Core business logic services
│   │   │   ├── __init__.py
│   │   │   ├── rag_service.py         # RAG implementation with FAISS
│   │   │   ├── trade_agent_service.py # CrewAI trade decision agents
│   │   │   ├── flowchart_service.py   # Groq LLaMA flowchart generation
│   │   │   ├── news_service.py        # News aggregation service
│   │   │   └── chat_service.py        # General chat & summary service
│   │   │
│   │   ├── agents/                    # CrewAI agent definitions
│   │   │   └── __init__.py
│   │   │
│   │   └── utils/                     # Utility functions
│   │       ├── __init__.py
│   │       └── file_manager.py        # File upload/management utilities
│   │
│   └── data/                          # Data storage directory
│       ├── uploads/                   # Uploaded PDF files
│       ├── vector_store/              # FAISS vector store persistence
│       └── trade_decisions.json       # Agent memory storage
│
├── frontend/                          # React Frontend
│   ├── setup.bat                      # Windows setup script
│   ├── package.json                   # Node.js dependencies
│   ├── tailwind.config.js             # Tailwind CSS configuration
│   ├── postcss.config.js              # PostCSS configuration
│   │
│   ├── public/                        # Static assets
│   │   └── index.html                 # HTML template
│   │
│   └── src/                           # React source code
│       ├── index.js                   # React application entry point
│       ├── index.css                  # Global styles with Tailwind
│       ├── App.js                     # Main application component
│       │
│       ├── components/                # React components
│       │   ├── Sidebar.js             # Navigation sidebar
│       │   ├── Header.js              # Application header
│       │   ├── MainChat.js            # General financial chat
│       │   ├── MessageBubble.js       # Chat message component
│       │   ├── LoadingSpinner.js      # Loading indicator
│       │   ├── TradeDecisionChat.js   # Trade analysis interface
│       │   ├── FlowchartGenerator.js  # Financial planning flowcharts
│       │   ├── NewsPanel.js           # Financial news feed
│       │   └── RAGChat.js             # Document analysis chat
│       │
│       ├── services/                  # API integration
│       │   └── api.js                 # Centralized API service
│       │
│       ├── hooks/                     # Custom React hooks
│       │   └── (placeholder)
│       │
│       └── pages/                     # Page components
│           └── (placeholder)
```

## Key Components Overview

### Backend Services
- **RAG Service**: Document processing, FAISS vector storage, Gemini integration
- **Trade Agent Service**: CrewAI orchestration, OpenAI analysis, decision memory
- **Flowchart Service**: Groq LLaMA integration, React Flow data generation
- **News Service**: Serper API integration, RSS feed parsing
- **Chat Service**: Gemini general chat, Ollama summary generation

### Frontend Components
- **Multi-service Interface**: Sidebar navigation between specialized services
- **Real-time Chat**: WebSocket-ready chat interfaces for all services
- **File Upload**: Drag-and-drop PDF upload with progress tracking
- **Interactive Flowcharts**: React Flow visualization for financial planning
- **News Aggregation**: Real-time news feed with company watchlists

### API Integration
- **Google Gemini 1.5 Flash**: General chat and RAG responses
- **OpenAI GPT**: Trade decision analysis and market research
- **Groq LLaMA**: Financial planning flowchart generation
- **IBM Granite (Ollama)**: Short summary generation
- **Serper API**: News aggregation and market research
- **Hugging Face**: Document embeddings for RAG

### Data Storage
- **FAISS Vector Store**: Persistent document embeddings
- **JSON Memory**: Agent decision history and learning
- **File System**: Uploaded document management
- **Session State**: Chat history and user preferences

## Technology Integrations

### AI/ML Stack
- **LangChain**: Document processing and chunking
- **FAISS**: Vector similarity search
- **CrewAI**: Multi-agent orchestration
- **Sentence Transformers**: Text embeddings

### Frontend Stack
- **React.js**: Component-based UI
- **Tailwind CSS**: Utility-first styling
- **React Flow**: Interactive flowchart visualization
- **Axios**: HTTP client for API communication

### Backend Stack
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and serialization
- **aiofiles**: Async file operations
- **python-multipart**: File upload handling
