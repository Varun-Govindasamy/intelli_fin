import React from "react";
import {
  ChatBubbleLeftRightIcon,
  ArrowTrendingUpIcon,
  DocumentChartBarIcon,
  NewspaperIcon,
  DocumentTextIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from "@heroicons/react/24/outline";

const Sidebar = ({ currentView, setCurrentView, isOpen, setIsOpen }) => {
  const menuItems = [
    {
      id: "main",
      label: "General Chat",
      icon: ChatBubbleLeftRightIcon,
      description: "Ask any financial questions",
    },
    {
      id: "trade",
      label: "Trade Decisions",
      icon: ArrowTrendingUpIcon,
      description: "AI-powered trade analysis",
    },
    {
      id: "flowchart",
      label: "Financial Planning",
      icon: DocumentChartBarIcon,
      description: "Generate savings/investment plans",
    },
    {
      id: "news",
      label: "Financial News",
      icon: NewspaperIcon,
      description: "Latest market updates",
    },
    {
      id: "rag",
      label: "Document Analysis",
      icon: DocumentTextIcon,
      description: "Upload and analyze financial reports",
    },
  ];

  return (
    <div
      className={`fixed left-0 top-0 h-full bg-white border-r border-gray-200 transition-all duration-300 z-30 ${
        isOpen ? "w-64" : "w-16"
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        {isOpen && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <ArrowTrendingUpIcon className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-xl font-bold text-gray-900">IntelliFinance</h1>
          </div>
        )}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
        >
          {isOpen ? (
            <ChevronLeftIcon className="w-5 h-5 text-gray-600" />
          ) : (
            <ChevronRightIcon className="w-5 h-5 text-gray-600" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;

          return (
            <button
              key={item.id}
              onClick={() => setCurrentView(item.id)}
              className={`w-full flex items-center space-x-3 px-3 py-3 rounded-lg transition-colors text-left group ${
                isActive
                  ? "bg-primary-50 text-primary-700 border-r-4 border-primary-600"
                  : "text-gray-700 hover:bg-gray-50"
              }`}
              title={!isOpen ? item.label : ""}
            >
              <Icon
                className={`w-5 h-5 flex-shrink-0 ${
                  isActive
                    ? "text-primary-600"
                    : "text-gray-500 group-hover:text-gray-700"
                }`}
              />

              {isOpen && (
                <div className="flex-1 min-w-0">
                  <p
                    className={`text-sm font-medium truncate ${
                      isActive ? "text-primary-900" : "text-gray-900"
                    }`}
                  >
                    {item.label}
                  </p>
                  <p
                    className={`text-xs truncate ${
                      isActive ? "text-primary-600" : "text-gray-500"
                    }`}
                  >
                    {item.description}
                  </p>
                </div>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      {isOpen && (
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-gray-50">
          <div className="text-xs text-gray-500 space-y-1">
            <p>IntelliFinance v1.0</p>
            <p>AI-Powered Financial Assistant</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;
