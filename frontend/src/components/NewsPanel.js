import React, { useState, useEffect, useCallback } from "react";
import {
  NewspaperIcon,
  ArrowTopRightOnSquareIcon,
  ArrowPathIcon,
} from "@heroicons/react/24/outline";
import { apiService } from "../services/api";
import toast from "react-hot-toast";
import LoadingSpinner from "./LoadingSpinner";

const NewsPanel = () => {
  const [generalNews, setGeneralNews] = useState([]);
  const [companyNews, setCompanyNews] = useState([]);
  const [watchedSymbols, setWatchedSymbols] = useState([
    "AAPL",
    "GOOGL",
    "MSFT",
    "TSLA",
  ]);
  const [newSymbol, setNewSymbol] = useState("");
  const [isLoadingGeneral, setIsLoadingGeneral] = useState(true);
  const [isLoadingCompany, setIsLoadingCompany] = useState(true);
  const [activeTab, setActiveTab] = useState("general");

  useEffect(() => {
    loadGeneralNews();
    loadCompanyNews();
  }, [loadCompanyNews]);

  useEffect(() => {
    if (watchedSymbols.length > 0) {
      loadCompanyNews();
    }
  }, [watchedSymbols, loadCompanyNews]);

  const loadGeneralNews = async () => {
    setIsLoadingGeneral(true);
    try {
      const response = await apiService.getGeneralNews();
      setGeneralNews(response.news || []);
    } catch (error) {
      console.error("Error loading general news:", error);
      toast.error("Failed to load general news");
    } finally {
      setIsLoadingGeneral(false);
    }
  };

  const loadCompanyNews = useCallback(async () => {
    if (watchedSymbols.length === 0) {
      setIsLoadingCompany(false);
      return;
    }

    setIsLoadingCompany(true);
    try {
      const response = await apiService.getCompanyNews(watchedSymbols);
      setCompanyNews(response.news || []);
    } catch (error) {
      console.error("Error loading company news:", error);
      toast.error("Failed to load company news");
    } finally {
      setIsLoadingCompany(false);
    }
  }, [watchedSymbols]);

  const addSymbol = (e) => {
    e.preventDefault();
    const symbol = newSymbol.trim().toUpperCase();

    if (!symbol) {
      toast.error("Please enter a valid symbol");
      return;
    }

    if (watchedSymbols.includes(symbol)) {
      toast.error("Symbol already in watchlist");
      return;
    }

    setWatchedSymbols((prev) => [...prev, symbol]);
    setNewSymbol("");
    toast.success(`Added ${symbol} to watchlist`);
  };

  const removeSymbol = (symbol) => {
    setWatchedSymbols((prev) => prev.filter((s) => s !== symbol));
    toast.success(`Removed ${symbol} from watchlist`);
  };

  const formatDate = (dateString) => {
    try {
      if (!dateString) return "Recent";

      const date = new Date(dateString);

      // Check if the date is valid
      if (isNaN(date.getTime())) {
        return "Recent";
      }

      // Check if the date is reasonable (not too far in the past or future)
      const now = new Date();
      const timeDiff = Math.abs(now.getTime() - date.getTime());
      const daysDiff = timeDiff / (1000 * 3600 * 24);

      if (daysDiff > 365) {
        return "Recent";
      }

      return (
        date.toLocaleDateString() +
        " " +
        date.toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        })
      );
    } catch (error) {
      console.warn("Date formatting error:", error);
      return "Recent";
    }
  };

  const NewsCard = ({ article }) => (
    <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-900 leading-tight flex-1 mr-3">
          {article.title}
        </h3>
        {article.url && (
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-shrink-0 p-1 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <ArrowTopRightOnSquareIcon className="w-4 h-4" />
          </a>
        )}
      </div>

      <p className="text-gray-700 mb-3 line-clamp-3">{article.description}</p>

      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center space-x-4">
          <span className="text-gray-500">
            {article.source || "Unknown Source"}
          </span>
          {article.symbol && (
            <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
              {article.symbol}
            </span>
          )}
        </div>
        <span className="text-gray-400">{formatDate(article.date)}</span>
      </div>
    </div>
  );

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              Financial News Feed
            </h2>
            <p className="text-sm text-gray-600">
              Stay updated with the latest market news
            </p>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={loadGeneralNews}
              disabled={isLoadingGeneral}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              title="Refresh General News"
            >
              <ArrowPathIcon
                className={`w-5 h-5 ${isLoadingGeneral ? "animate-spin" : ""}`}
              />
            </button>
            <button
              onClick={loadCompanyNews}
              disabled={isLoadingCompany}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              title="Refresh Company News"
            >
              <ArrowPathIcon
                className={`w-5 h-5 ${isLoadingCompany ? "animate-spin" : ""}`}
              />
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="flex">
          <button
            onClick={() => setActiveTab("general")}
            className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === "general"
                ? "border-primary-600 text-primary-600"
                : "border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300"
            }`}
          >
            General Financial News
          </button>
          <button
            onClick={() => setActiveTab("company")}
            className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === "company"
                ? "border-primary-600 text-primary-600"
                : "border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300"
            }`}
          >
            Company Watchlist ({watchedSymbols.length})
          </button>
        </div>
      </div>

      {/* Company Watchlist Management */}
      {activeTab === "company" && (
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="flex items-center space-x-4 mb-3">
            <form onSubmit={addSymbol} className="flex items-center space-x-2">
              <input
                type="text"
                value={newSymbol}
                onChange={(e) => setNewSymbol(e.target.value)}
                placeholder="Add symbol (e.g., AAPL)"
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
              >
                Add
              </button>
            </form>
          </div>

          <div className="flex flex-wrap gap-2">
            {watchedSymbols.map((symbol) => (
              <span
                key={symbol}
                className="inline-flex items-center px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm"
              >
                {symbol}
                <button
                  onClick={() => removeSymbol(symbol)}
                  className="ml-2 text-gray-500 hover:text-red-600 transition-colors"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* News Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === "general" && (
          <div className="space-y-4">
            {isLoadingGeneral ? (
              <LoadingSpinner message="Loading general financial news..." />
            ) : generalNews.length > 0 ? (
              generalNews.map((article, index) => (
                <NewsCard key={index} article={article} />
              ))
            ) : (
              <div className="text-center py-12">
                <NewspaperIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No News Available
                </h3>
                <p className="text-gray-600">
                  Unable to load financial news at the moment.
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === "company" && (
          <div className="space-y-4">
            {isLoadingCompany ? (
              <LoadingSpinner message="Loading company-specific news..." />
            ) : companyNews.length > 0 ? (
              companyNews.map((article, index) => (
                <NewsCard key={index} article={article} />
              ))
            ) : watchedSymbols.length > 0 ? (
              <div className="text-center py-12">
                <NewspaperIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Company News Available
                </h3>
                <p className="text-gray-600">
                  No recent news found for the companies in your watchlist.
                </p>
              </div>
            ) : (
              <div className="text-center py-12">
                <NewspaperIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Companies in Watchlist
                </h3>
                <p className="text-gray-600">
                  Add some company symbols to get personalized news updates.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default NewsPanel;
