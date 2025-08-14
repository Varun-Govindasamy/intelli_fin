import React, { useState, useRef, useEffect } from "react";
import {
  CurrencyDollarIcon,
  ChartBarIcon,
  ClockIcon,
  BuildingOfficeIcon,
  ChevronUpIcon,
  ChevronDownIcon,
} from "@heroicons/react/24/outline";
import { apiService } from "../services/api";
import toast from "react-hot-toast";
import LoadingSpinner from "./LoadingSpinner";

const TradeDecisionChat = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Portfolio analysis states
  const [budget, setBudget] = useState("");
  const [riskLevel, setRiskLevel] = useState("medium");
  const [timeHorizon, setTimeHorizon] = useState("medium");
  const [sectorPreferences, setSectorPreferences] = useState("");
  const [portfolioSymbols, setPortfolioSymbols] = useState("");
  const [portfolioResults, setPortfolioResults] = useState(null);
  const [isPortfolioFormCollapsed, setIsPortfolioFormCollapsed] =
    useState(false);
  const [isGeneratingPortfolioSummary, setIsGeneratingPortfolioSummary] =
    useState(false);

  const analysisEndRef = useRef(null);
  useEffect(() => {
    analysisEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [portfolioResults]);

  const handlePortfolioAnalysis = async (e) => {
    e.preventDefault();

    if (!budget || !portfolioSymbols.trim() || isAnalyzing) {
      toast.error("Please fill in budget and stock symbols");
      return;
    }

    setIsAnalyzing(true);
    setIsPortfolioFormCollapsed(true); // Collapse the form during analysis

    try {
      const response = await apiService.comprehensiveTradeAnalysis(
        parseFloat(budget),
        riskLevel,
        timeHorizon,
        sectorPreferences,
        portfolioSymbols.trim()
      );

      setPortfolioResults(response);
      toast.success("Portfolio analysis completed!");
    } catch (error) {
      console.error("Error analyzing portfolio:", error);
      toast.error("Failed to analyze portfolio. Please try again.");
      setIsPortfolioFormCollapsed(false); // Expand form if there's an error
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClearPortfolioResults = () => {
    setPortfolioResults(null);
    setIsPortfolioFormCollapsed(false); // Expand form when clearing results
  };

  const generatePortfolioSummary = async () => {
    try {
      setIsGeneratingPortfolioSummary(true);

      // Create a comprehensive text of the portfolio analysis
      const analysisText = `
        Portfolio Analysis Results:
        Budget: $${portfolioResults.user_profile?.budget?.toLocaleString()}
        Risk Level: ${portfolioResults.user_profile?.risk_level}
        Time Horizon: ${portfolioResults.user_profile?.time_horizon}
        
        Portfolio Analysis:
        Total Risk Score: ${
          portfolioResults.portfolio_analysis?.total_risk_score
        }
        Growth Potential: ${
          portfolioResults.portfolio_analysis?.growth_potential
        }
        Market Sentiment: ${
          portfolioResults.portfolio_analysis?.market_sentiment
        }
        Risk Level: ${portfolioResults.portfolio_analysis?.risk_level}
        
        Top Recommendations:
        ${portfolioResults.recommendations
          ?.map(
            (rec) =>
              `${rec.symbol}: ${
                rec.allocation_percentage
              }% allocation ($${rec.investment_amount?.toLocaleString()}) - Growth: ${
                rec.growth_score
              }, Risk: ${rec.risk_score}`
          )
          .join("\n")}
        
        Risk Factors:
        ${portfolioResults.risk_factors?.join("\n")}
        
        Summary: ${portfolioResults.summary}
      `;

      const response = await apiService.generateSummary(analysisText);

      setPortfolioResults((prev) => ({
        ...prev,
        generated_summary: response.summary,
      }));

      toast.success("Portfolio summary generated successfully");
    } catch (error) {
      console.error("Error generating portfolio summary:", error);
      toast.error("Failed to generate portfolio summary");
    } finally {
      setIsGeneratingPortfolioSummary(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              Portfolio Analysis Assistant
            </h2>
            <p className="text-sm text-gray-600">
              AI-powered portfolio analysis using CrewAI agents
            </p>
          </div>
        </div>
      </div>

      {/* Analysis Form */}
      <div className="bg-white border-b border-gray-200">
        {/* Portfolio Analysis Form */}
        <div className="p-4">
          {/* Toggle Button for Portfolio Form */}
          {(isPortfolioFormCollapsed || portfolioResults) && (
            <div className="mb-4 flex justify-between items-center">
              <span className="text-sm text-gray-600">
                {isAnalyzing ? "Analyzing your portfolio..." : "Portfolio form"}
              </span>
              <button
                type="button"
                onClick={() =>
                  setIsPortfolioFormCollapsed(!isPortfolioFormCollapsed)
                }
                className="flex items-center space-x-1 px-3 py-1 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
                disabled={isAnalyzing}
              >
                <span>
                  {isPortfolioFormCollapsed ? "Show Form" : "Hide Form"}
                </span>
                {isPortfolioFormCollapsed ? (
                  <ChevronDownIcon className="w-4 h-4" />
                ) : (
                  <ChevronUpIcon className="w-4 h-4" />
                )}
              </button>
            </div>
          )}

          {/* Collapsible Form with smooth transition */}
          <div
            className={`transition-all duration-300 ease-in-out overflow-hidden ${
              isPortfolioFormCollapsed
                ? "max-h-0 opacity-0"
                : "max-h-96 opacity-100"
            }`}
          >
            {!isPortfolioFormCollapsed && (
              <form onSubmit={handlePortfolioAnalysis} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Budget */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <CurrencyDollarIcon className="w-4 h-4 inline mr-1" />
                      Investment Budget
                    </label>
                    <input
                      type="number"
                      value={budget}
                      onChange={(e) => setBudget(e.target.value)}
                      placeholder="e.g., 10000"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      disabled={isAnalyzing}
                      min="100"
                      step="100"
                    />
                  </div>

                  {/* Risk Level */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <ChartBarIcon className="w-4 h-4 inline mr-1" />
                      Risk Tolerance
                    </label>
                    <select
                      value={riskLevel}
                      onChange={(e) => setRiskLevel(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      disabled={isAnalyzing}
                    >
                      <option value="low">Conservative (Low Risk)</option>
                      <option value="medium">Moderate (Medium Risk)</option>
                      <option value="high">Aggressive (High Risk)</option>
                    </select>
                  </div>

                  {/* Time Horizon */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <ClockIcon className="w-4 h-4 inline mr-1" />
                      Investment Time Horizon
                    </label>
                    <select
                      value={timeHorizon}
                      onChange={(e) => setTimeHorizon(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      disabled={isAnalyzing}
                    >
                      <option value="short">Short Term (&lt; 1 year)</option>
                      <option value="medium">Medium Term (1-5 years)</option>
                      <option value="long">Long Term (5+ years)</option>
                    </select>
                  </div>

                  {/* Sector Preferences */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <BuildingOfficeIcon className="w-4 h-4 inline mr-1" />
                      Preferred Sectors (Optional)
                    </label>
                    <input
                      type="text"
                      value={sectorPreferences}
                      onChange={(e) => setSectorPreferences(e.target.value)}
                      placeholder="e.g., Technology, Healthcare, Finance"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      disabled={isAnalyzing}
                    />
                  </div>
                </div>

                {/* Stock Symbols */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Stock Symbols to Analyze
                  </label>
                  <input
                    type="text"
                    value={portfolioSymbols}
                    onChange={(e) => setPortfolioSymbols(e.target.value)}
                    placeholder="e.g., AAPL, GOOGL, MSFT, TSLA, NVDA"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={isAnalyzing}
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    Enter comma-separated stock symbols
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={!budget || !portfolioSymbols.trim() || isAnalyzing}
                  className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isAnalyzing ? (
                    <div className="flex items-center justify-center">
                      <div className="spinner mr-2" />
                      Analyzing Portfolio...
                    </div>
                  ) : (
                    "Analyze Portfolio"
                  )}
                </button>
              </form>
            )}
          </div>
        </div>

        {/* Analysis Results */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
          {/* Portfolio Results - Only show when portfolio tab is active */}
          {portfolioResults && (
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
              {/* Sticky Header with Clear Button */}
              <div className="sticky top-0 bg-white flex items-center justify-between p-4 border-b border-gray-200 z-10">
                <h3 className="text-lg font-semibold text-gray-900">
                  📊 Portfolio Analysis Results
                </h3>
                <button
                  onClick={handleClearPortfolioResults}
                  className="px-3 py-1 text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  ✕ Clear
                </button>
              </div>

              {/* Scrollable Content */}
              <div className="max-h-96 overflow-y-auto">
                <div className="p-4 space-y-4">
                  {/* User Profile Summary */}
                  <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-semibold text-gray-800 mb-2">
                      Investment Profile
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Budget:</span>
                        <span className="font-medium ml-2">
                          $
                          {portfolioResults.user_profile?.budget?.toLocaleString()}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Risk Level:</span>
                        <span className="font-medium ml-2 capitalize">
                          {portfolioResults.user_profile?.risk_level}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Time Horizon:</span>
                        <span className="font-medium ml-2 capitalize">
                          {portfolioResults.user_profile?.time_horizon}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Sectors:</span>
                        <span className="font-medium ml-2">
                          {portfolioResults.user_profile?.sector_preferences?.join(
                            ", "
                          ) || "None"}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Portfolio Analysis */}
                  <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <h4 className="font-semibold text-blue-800 mb-3">
                      Portfolio Overview
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-blue-600">Risk Score:</span>
                        <span className="font-medium ml-2">
                          {
                            portfolioResults.portfolio_analysis
                              ?.total_risk_score
                          }
                        </span>
                      </div>
                      <div>
                        <span className="text-blue-600">Growth Potential:</span>
                        <span className="font-medium ml-2">
                          {(
                            portfolioResults.portfolio_analysis
                              ?.growth_potential * 100
                          )?.toFixed(1)}
                          %
                        </span>
                      </div>
                      <div>
                        <span className="text-blue-600">Market Sentiment:</span>
                        <span className="font-medium ml-2">
                          {(
                            portfolioResults.portfolio_analysis
                              ?.market_sentiment * 100
                          )?.toFixed(1)}
                          %
                        </span>
                      </div>
                      <div>
                        <span className="text-blue-600">Risk Level:</span>
                        <span className="font-medium ml-2">
                          {portfolioResults.portfolio_analysis?.risk_level}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Investment Recommendations */}
                  <div className="mb-6">
                    <h4 className="font-semibold text-gray-800 mb-3">
                      Investment Recommendations
                    </h4>
                    <div className="space-y-3">
                      {portfolioResults.recommendations?.map((rec, index) => (
                        <div
                          key={index}
                          className="p-4 border border-gray-200 rounded-lg"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-3">
                              <span className="font-semibold text-lg">
                                {rec.symbol}
                              </span>
                              <span className="text-green-600 font-medium">
                                {rec.allocation_percentage}%
                              </span>
                              <span className="text-gray-600">
                                ${rec.investment_amount?.toLocaleString()}
                              </span>
                            </div>
                            <span className="text-gray-600">
                              ${rec.current_price?.toFixed(2)}
                            </span>
                          </div>
                          <div className="grid grid-cols-3 gap-4 text-sm mb-2">
                            <div>
                              <span className="text-gray-600">Growth:</span>
                              <span className="font-medium ml-2">
                                {rec.growth_score}
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-600">Risk:</span>
                              <span className="font-medium ml-2">
                                {rec.risk_score}
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-600">Sentiment:</span>
                              <span className="font-medium ml-2">
                                {rec.sentiment_score}
                              </span>
                            </div>
                          </div>
                          <p className="text-sm text-gray-700">
                            {rec.reasoning}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Risk Factors */}
                  <div className="mb-6">
                    <h4 className="font-semibold text-red-800 mb-3">
                      Risk Factors
                    </h4>
                    <div className="space-y-2">
                      {portfolioResults.risk_factors?.map((factor, index) => (
                        <div key={index} className="flex items-start space-x-2">
                          <span className="text-red-500 mt-1">⚠️</span>
                          <span className="text-sm text-gray-700">
                            {factor}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* AI Summary Section */}
                  {portfolioResults.generated_summary ? (
                    <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                      <h4 className="font-semibold text-blue-800 mb-2">
                        AI Generated Summary (Granite 3.3:2b)
                      </h4>
                      <p className="text-blue-800">
                        {portfolioResults.generated_summary}
                      </p>
                    </div>
                  ) : (
                    <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-gray-800">
                          Generate AI Summary
                        </h4>
                        <button
                          onClick={generatePortfolioSummary}
                          disabled={isGeneratingPortfolioSummary}
                          className={`px-4 py-2 text-sm rounded transition-colors flex items-center space-x-2 ${
                            isGeneratingPortfolioSummary
                              ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                              : "bg-blue-600 text-white hover:bg-blue-700"
                          }`}
                        >
                          {isGeneratingPortfolioSummary ? (
                            <>
                              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                              <span>Generating with Granite 3.3:2b...</span>
                            </>
                          ) : (
                            <>
                              <span>🤖</span>
                              <span>Generate Summary</span>
                            </>
                          )}
                        </button>
                      </div>
                      <p className="text-sm text-gray-600 mt-2">
                        Click to generate an AI-powered summary of your
                        portfolio analysis using the Granite 3.3:2b model.
                      </p>
                    </div>
                  )}

                  {/* Clear Results Button */}
                  <div className="mt-4 flex justify-end">
                    <button
                      onClick={handleClearPortfolioResults}
                      className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      Clear Results
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {isAnalyzing && (
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <LoadingSpinner message="AI agents are analyzing the portfolio..." />
              <div className="mt-4 text-sm text-gray-600 space-y-2">
                <p>• Research Agent: Gathering market data for all symbols</p>
                <p>
                  • Analysis Agent: Performing comprehensive portfolio analysis
                </p>
                <p>• Decision Agent: Formulating recommendations</p>
              </div>
            </div>
          )}

          <div ref={analysisEndRef} />
        </div>
      </div>
    </div>
  );
};

export default TradeDecisionChat;
