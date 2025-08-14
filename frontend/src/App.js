import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import Sidebar from "./components/Sidebar";
import MainChat from "./components/MainChat";
import TradeDecisionChat from "./components/TradeDecisionChat";
import FlowchartGenerator from "./components/FlowchartGenerator";
import NewsPanel from "./components/NewsPanel";
import RAGChat from "./components/RAGChat";
import Header from "./components/Header";
import "./index.css";

function App() {
  const [currentView, setCurrentView] = useState("main");
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const renderMainContent = () => {
    switch (currentView) {
      case "main":
        return <MainChat />;
      case "trade":
        return <TradeDecisionChat />;
      case "flowchart":
        return <FlowchartGenerator />;
      case "news":
        return <NewsPanel />;
      case "rag":
        return <RAGChat />;
      default:
        return <MainChat />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Toaster position="top-right" />

      {/* Sidebar */}
      <Sidebar
        currentView={currentView}
        setCurrentView={setCurrentView}
        isOpen={sidebarOpen}
        setIsOpen={setSidebarOpen}
      />

      {/* Main Content */}
      <div
        className={`flex-1 flex flex-col transition-all duration-300 ${
          sidebarOpen ? "ml-64" : "ml-16"
        }`}
      >
        {/* Header */}
        <Header
          currentView={currentView}
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
        />

        {/* Main Content Area */}
        <main className="flex-1 overflow-hidden">{renderMainContent()}</main>
      </div>
    </div>
  );
}

export default App;
