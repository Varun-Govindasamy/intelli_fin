import React from "react";
import { Bars3Icon } from "@heroicons/react/24/outline";

const Header = ({ currentView, sidebarOpen, setSidebarOpen }) => {
  const getViewTitle = () => {
    switch (currentView) {
      case "main":
        return "General Financial Chat";
      case "trade":
        return "Trade Decision Assistant";
      case "flowchart":
        return "Financial Planning & Flowcharts";
      case "news":
        return "Financial News Feed";
      case "rag":
        return "Document Analysis & RAG";
      default:
        return "IntelliFinance";
    }
  };

  const getViewDescription = () => {
    switch (currentView) {
      case "main":
        return "Ask any financial questions and get AI-powered insights";
      case "trade":
        return "Get comprehensive trade analysis and investment recommendations";
      case "flowchart":
        return "Generate personalized financial planning workflows";
      case "news":
        return "Stay updated with the latest financial market news";
      case "rag":
        return "Upload and analyze financial documents with AI";
      default:
        return "Your AI-powered financial assistant";
    }
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {!sidebarOpen && (
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors lg:hidden"
            >
              <Bars3Icon className="w-5 h-5 text-gray-600" />
            </button>
          )}

          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {getViewTitle()}
            </h1>
            <p className="text-sm text-gray-600">{getViewDescription()}</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {/* Status indicator */}
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-600">AI Services Active</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
