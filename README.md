# IntelliFinance - AI-Powered Financial Insights and Decision Support System

A comprehensive AI-powered financial assistant that provides financial analysis, trade decision support, document analysis, news aggregation, and financial planning workflows.

## 🚀 Features

### 1. **General Financial Chat**
- AI-powered financial Q&A using Google Gemini 1.5 Flash
- Conversational interface for financial advice and insights
- Real-time responses to financial queries

### 2. **Trade Decision Assistant**
- Comprehensive trade analysis using CrewAI agents
- Multi-agent workflow: Research → Analysis → Decision
- Integration with OpenAI API for market analysis
- Decision history tracking with memory
- Short summary generation using IBM Granite via Ollama

### 3. **RAG-Based Document Analysis**
- Upload and analyze multiple PDF financial reports
- Persistent FAISS vector storage
- Context-aware querying using Hugging Face embeddings
- Intelligent document chunking with LangChain

### 4. **Financial Planning Flowcharts**
- AI-generated financial planning workflows
- Interactive flowchart visualization using React Flow
- Powered by Groq API (LLaMA models)
- Customizable goals, time horizons, and risk tolerance

### 5. **Financial News Feed**
- Real-time financial news aggregation
- Company-specific news tracking
- Multiple news sources integration
- Personalized company watchlists

## 🛠 Technology Stack

### Backend
- **Framework**: FastAPI
- **LLM APIs**: 
  - Google Gemini 1.5 Flash (general chat & RAG)
  - OpenAI GPT (trade analysis)
  - Groq API with LLaMA (flowchart generation)
  - IBM Granite 2B via Ollama (summaries)
- **AI Orchestration**: CrewAI Framework
- **Vector Store**: FAISS (persistent)
- **Embeddings**: Hugging Face Transformers
- **Document Processing**: LangChain
- **News & Research**: Serper API

### Frontend
- **Framework**: React.js
- **Styling**: Tailwind CSS
- **Visualization**: React Flow
- **HTTP Client**: Axios
- **File Upload**: React Dropzone
- **Notifications**: React Hot Toast
- **Icons**: Heroicons

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Ollama (for IBM Granite model)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_API_KEY=your_gemini_api_key
   GROQ_API_KEY=your_groq_api_key
   SERPER_API_KEY=your_serper_api_key
   OLLAMA_BASE_URL=http://localhost:11434
   ```

5. **Install and run Ollama (for IBM Granite)**
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull granite-code:3b
   # or any compatible model
   ```

6. **Run the backend**
   ```bash
   python main.py
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## 🔑 API Keys Required

### Required APIs
1. **OpenAI API**: For trade decision analysis
2. **Google Gemini API**: For general chat and RAG responses
3. **Groq API**: For flowchart generation using LLaMA
4. **Serper API**: For news aggregation and market research

### Optional APIs
- **Ollama**: For local IBM Granite model (summary generation)

## 🎯 Usage Guide

### 1. General Chat
- Navigate to the main chat interface
- Ask any financial questions
- Get AI-powered insights and advice

### 2. Trade Analysis
- Go to "Trade Decisions" section
- Enter a stock symbol (e.g., AAPL, TSLA)
- Select analysis type
- Get comprehensive buy/sell/hold recommendations

### 3. Document Analysis
- Navigate to "Document Analysis" section
- Upload PDF financial reports (up to 5 files)
- Ask questions about the uploaded documents
- Get context-aware responses based on document content

### 4. Financial Planning
- Go to "Financial Planning" section
- Enter your financial goal
- Select time horizon and risk tolerance
- Generate interactive planning flowchart

### 5. News Feed
- Visit "Financial News" section
- View general financial news
- Add companies to your watchlist
- Get company-specific news updates

## 🏗 Architecture

### Backend Architecture
```
backend/
├── app/
│   ├── services/           # Core business logic
│   │   ├── rag_service.py      # RAG implementation
│   │   ├── trade_agent_service.py  # CrewAI agents
│   │   ├── flowchart_service.py    # Flowchart generation
│   │   ├── news_service.py         # News aggregation
│   │   └── chat_service.py         # General chat
│   ├── agents/             # CrewAI agent definitions
│   └── utils/              # Utility functions
├── data/                   # Data storage
│   ├── uploads/            # Uploaded files
│   ├── vector_store/       # FAISS indices
│   └── trade_decisions.json # Agent memory
└── main.py                 # FastAPI application
```

### Frontend Architecture
```
frontend/src/
├── components/             # React components
│   ├── Sidebar.js             # Navigation sidebar
│   ├── MainChat.js            # General chat interface
│   ├── TradeDecisionChat.js   # Trade analysis UI
│   ├── FlowchartGenerator.js  # Financial planning
│   ├── NewsPanel.js           # News feed
│   └── RAGChat.js             # Document analysis
├── services/               # API integration
│   └── api.js                 # API service layer
└── App.js                  # Main application
```

## 🔒 Security & Privacy

- API keys stored in environment variables
- File uploads validated and size-limited
- No sensitive data persisted without encryption
- CORS properly configured
- Input validation on all endpoints

## 🚀 Deployment

### Backend Deployment
1. Set up production environment variables
2. Configure CORS for production domain
3. Use production WSGI server (e.g., Gunicorn)
4. Set up reverse proxy (Nginx)
5. Configure SSL certificates

### Frontend Deployment
1. Build production bundle: `npm run build`
2. Serve static files through CDN or web server
3. Configure environment variables for API endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API endpoints at http://localhost:8000/docs

## 🎉 Acknowledgments

- OpenAI for GPT models
- Google for Gemini API
- Groq for LLaMA API access
- CrewAI for agent orchestration
- LangChain for document processing
- React Flow for flowchart visualization
