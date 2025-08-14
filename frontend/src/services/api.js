import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(
      `Making ${config.method?.toUpperCase()} request to ${config.url}`
    );
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const apiService = {
  // General chat
  generalChat: async (message) => {
    const formData = new FormData();
    formData.append("message", message);
    const response = await api.post("/api/chat/general", formData);
    return response.data;
  },

  // RAG service
  uploadDocuments: async (files) => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });
    const response = await api.post("/api/rag/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  queryRAG: async (query) => {
    const formData = new FormData();
    formData.append("query", query);
    const response = await api.post("/api/rag/query", formData);
    return response.data;
  },

  // Trade decision service
  analyzeTrade: async (symbol, analysisType = "comprehensive") => {
    const formData = new FormData();
    formData.append("company_symbol", symbol);
    formData.append("analysis_type", analysisType);
    const response = await api.post("/api/trade/analyze", formData);
    return response.data;
  },

  getTradeHistory: async () => {
    const response = await api.get("/api/trade/history");
    return response.data;
  },

  // Comprehensive trade analysis
  comprehensiveTradeAnalysis: async (
    budget,
    riskLevel,
    timeHorizon,
    sectorPreferences,
    symbols
  ) => {
    const formData = new FormData();
    formData.append("budget", budget);
    formData.append("risk_level", riskLevel);
    formData.append("time_horizon", timeHorizon);
    formData.append("sector_preferences", sectorPreferences);
    formData.append("symbols", symbols);
    const response = await api.post(
      "/api/trade/comprehensive-analysis",
      formData
    );
    return response.data;
  },

  // Flowchart service
  generateFlowchart: async (
    goal,
    timeHorizon = "1 year",
    riskTolerance = "moderate"
  ) => {
    const formData = new FormData();
    formData.append("financial_goal", goal);
    formData.append("time_horizon", timeHorizon);
    formData.append("risk_tolerance", riskTolerance);
    const response = await api.post("/api/flowchart/generate", formData);
    return response.data;
  },

  // News service
  getCompanyNews: async (symbols) => {
    const symbolsString = Array.isArray(symbols) ? symbols.join(",") : symbols;
    const response = await api.get(
      `/api/news/companies?symbols=${symbolsString}`
    );
    return response.data;
  },

  getGeneralNews: async () => {
    const response = await api.get("/api/news/general");
    return response.data;
  },

  // Summary service
  generateSummary: async (content) => {
    const formData = new FormData();
    formData.append("content", content);
    const response = await api.post("/api/chat/summary", formData);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get("/health");
    return response.data;
  },
};

export default api;
