import React, { useState, useCallback } from "react";
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  ConnectionLineType,
  Handle,
  Position,
  Panel,
} from "reactflow";
import "reactflow/dist/style.css";
import {
  PlayIcon,
  ChartBarIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  CogIcon,
  FlagIcon,
  ClockIcon,
  BanknotesIcon,
  ArrowPathIcon,
  SparklesIcon,
  TrophyIcon,
  RocketLaunchIcon,
  ChevronDownIcon,
} from "@heroicons/react/24/outline";
import { apiService } from "../services/api";
import toast from "react-hot-toast";
import LoadingSpinner from "./LoadingSpinner";

const FlowchartGenerator = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [formData, setFormData] = useState({
    financial_goal: "",
    time_horizon: "1 year",
    risk_tolerance: "moderate",
  });
  const [generatedPlan, setGeneratedPlan] = useState("");
  const [showPlanDetails, setShowPlanDetails] = useState(false);
  const [isFormCollapsed, setIsFormCollapsed] = useState(false);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const generateFlowchart = async (e) => {
    e.preventDefault();

    if (!formData.financial_goal.trim()) {
      toast.error("Please enter a financial goal");
      return;
    }

    setIsGenerating(true);
    setIsFormCollapsed(true); // Collapse form when generating

    try {
      const response = await apiService.generateFlowchart(
        formData.financial_goal,
        formData.time_horizon,
        formData.risk_tolerance
      );

      if (response.nodes && response.edges) {
        setNodes(response.nodes);
        setEdges(response.edges);
        setGeneratedPlan(response.metadata?.generated_plan || "");
        setShowPlanDetails(true); // Auto-show plan details when generated
        toast.success("Flowchart generated successfully!");
      } else {
        throw new Error("Invalid response format");
      }
    } catch (error) {
      console.error("Error generating flowchart:", error);
      toast.error("Failed to generate flowchart. Please try again.");
      setIsFormCollapsed(false); // Expand form if there's an error

      // Create a basic fallback flowchart
      createFallbackFlowchart();
    } finally {
      setIsGenerating(false);
    }
  };

  const createFallbackFlowchart = () => {
    const fallbackNodes = [
      {
        id: "start",
        type: "startNode",
        position: { x: 400, y: 50 },
        data: {
          label: "Define Financial Goal",
          description: formData.financial_goal,
          icon: FlagIcon,
        },
      },
      {
        id: "assess",
        type: "processNode",
        position: { x: 150, y: 250 },
        data: {
          label: "Current Assessment",
          description: "Evaluate income, expenses, assets & debts",
          icon: ChartBarIcon,
        },
      },
      {
        id: "timeline",
        type: "processNode",
        position: { x: 400, y: 250 },
        data: {
          label: "Set Timeline",
          description: `${formData.time_horizon} planning horizon`,
          icon: ClockIcon,
        },
      },
      {
        id: "strategy",
        type: "processNode",
        position: { x: 650, y: 250 },
        data: {
          label: "Investment Strategy",
          description: `${formData.risk_tolerance} risk approach`,
          icon: BanknotesIcon,
        },
      },
      {
        id: "plan",
        type: "decisionNode",
        position: { x: 400, y: 450 },
        data: {
          label: "Create Action Plan",
          description: "Monthly savings & investment allocation",
          icon: DocumentTextIcon,
        },
      },
      {
        id: "implement",
        type: "processNode",
        position: { x: 200, y: 650 },
        data: {
          label: "Execute Plan",
          description: "Start saving & investing according to plan",
          icon: PlayIcon,
        },
      },
      {
        id: "monitor",
        type: "processNode",
        position: { x: 600, y: 650 },
        data: {
          label: "Monitor Progress",
          description: "Track performance & adjust as needed",
          icon: ArrowPathIcon,
        },
      },
      {
        id: "end",
        type: "endNode",
        position: { x: 400, y: 850 },
        data: {
          label: "Achieve Goal",
          description: "Successfully reach financial objective",
          icon: CheckCircleIcon,
        },
      },
    ];

    const fallbackEdges = [
      {
        id: "e1",
        source: "start",
        target: "assess",
        type: "smoothstep",
        animated: true,
        style: {
          stroke: "url(#gradient1)",
          strokeWidth: 3,
          filter: "drop-shadow(0 2px 4px rgba(59, 130, 246, 0.3))",
        },
      },
      {
        id: "e2",
        source: "start",
        target: "timeline",
        type: "smoothstep",
        animated: true,
        style: {
          stroke: "url(#gradient2)",
          strokeWidth: 3,
          filter: "drop-shadow(0 2px 4px rgba(59, 130, 246, 0.3))",
        },
      },
      {
        id: "e3",
        source: "start",
        target: "strategy",
        type: "smoothstep",
        animated: true,
        style: {
          stroke: "url(#gradient3)",
          strokeWidth: 3,
          filter: "drop-shadow(0 2px 4px rgba(59, 130, 246, 0.3))",
        },
      },
      {
        id: "e4",
        source: "assess",
        target: "plan",
        type: "smoothstep",
        animated: true,
        style: {
          stroke: "#10b981",
          strokeWidth: 3,
          filter: "drop-shadow(0 2px 4px rgba(16, 185, 129, 0.3))",
        },
      },
      {
        id: "e5",
        source: "timeline",
        target: "plan",
        type: "smoothstep",
        animated: true,
        style: {
          stroke: "#10b981",
          strokeWidth: 3,
          filter: "drop-shadow(0 2px 4px rgba(16, 185, 129, 0.3))",
        },
      },
      {
        id: "e6",
        source: "strategy",
        target: "plan",
        type: "smoothstep",
        animated: true,
        style: {
          stroke: "#10b981",
          strokeWidth: 3,
          filter: "drop-shadow(0 2px 4px rgba(16, 185, 129, 0.3))",
        },
      },
      {
        id: "e7",
        source: "plan",
        target: "implement",
        type: "smoothstep",
        animated: true,
        style: {
          stroke: "#f59e0b",
          strokeWidth: 3,
          filter: "drop-shadow(0 2px 4px rgba(245, 158, 11, 0.3))",
        },
      },
      {
        id: "e8",
        source: "plan",
        target: "monitor",
        type: "smoothstep",
        animated: true,
        style: {
          stroke: "#f59e0b",
          strokeWidth: 3,
          filter: "drop-shadow(0 2px 4px rgba(245, 158, 11, 0.3))",
        },
      },
      {
        id: "e9",
        source: "implement",
        target: "end",
        type: "smoothstep",
        animated: true,
        style: {
          stroke: "#8b5cf6",
          strokeWidth: 3,
          filter: "drop-shadow(0 2px 4px rgba(139, 92, 246, 0.3))",
        },
      },
      {
        id: "e10",
        source: "monitor",
        target: "end",
        type: "smoothstep",
        animated: true,
        style: {
          stroke: "#8b5cf6",
          strokeWidth: 3,
          filter: "drop-shadow(0 2px 4px rgba(139, 92, 246, 0.3))",
        },
      },
      {
        id: "e11",
        source: "monitor",
        target: "plan",
        type: "smoothstep",
        animated: true,
        style: {
          stroke: "#6366f1",
          strokeWidth: 2,
          strokeDasharray: "8,4",
          filter: "drop-shadow(0 1px 2px rgba(99, 102, 241, 0.3))",
        },
        label: "Adjust if needed",
        labelStyle: {
          fill: "#6366f1",
          fontWeight: 600,
          fontSize: "12px",
        },
        labelBgStyle: {
          fill: "white",
          fillOpacity: 0.9,
          rx: 8,
        },
      },
    ];

    setNodes(fallbackNodes);
    setEdges(fallbackEdges);
    setGeneratedPlan(
      "Interactive financial planning workflow created with assessment, planning, implementation, and monitoring phases."
    );
    setShowPlanDetails(true); // Auto-show plan details
    setIsFormCollapsed(true); // Collapse form when fallback flowchart is created
  };

  const clearFlowchart = () => {
    setNodes([]);
    setEdges([]);
    setGeneratedPlan("");
    setShowPlanDetails(false);
    setIsFormCollapsed(false); // Expand form when clearing
    setFormData({
      financial_goal: "",
      time_horizon: "1 year",
      risk_tolerance: "moderate",
    });
  };

  // Custom Node Components
  const StartNode = ({ data }) => {
    const IconComponent = data.icon || RocketLaunchIcon;
    return (
      <div className="relative group">
        <Handle type="source" position={Position.Bottom} className="w-3 h-3" />
        <div className="px-6 py-4 bg-gradient-to-br from-emerald-500 via-green-500 to-teal-600 text-white rounded-2xl shadow-xl border-2 border-emerald-400 min-w-[220px] hover:shadow-2xl transition-all duration-300 transform hover:scale-105 group-hover:rotate-1">
          <div className="flex items-center space-x-3 mb-3">
            <div className="bg-white bg-opacity-20 rounded-xl p-2.5 backdrop-blur-sm">
              <IconComponent className="w-6 h-6" />
            </div>
            <div className="font-bold text-lg">{data.label}</div>
            <SparklesIcon className="w-5 h-5 text-emerald-200 animate-pulse" />
          </div>
          {data.description && (
            <div className="text-sm text-emerald-100 leading-relaxed font-medium">
              {data.description}
            </div>
          )}
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-400 rounded-full animate-ping"></div>
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-300 rounded-full"></div>
        </div>
      </div>
    );
  };

  const ProcessNode = ({ data }) => {
    const IconComponent = data.icon || CogIcon;
    return (
      <div className="relative group">
        <Handle type="target" position={Position.Top} className="w-3 h-3" />
        <Handle type="source" position={Position.Bottom} className="w-3 h-3" />
        <div className="px-5 py-4 bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600 text-white rounded-xl shadow-xl border-2 border-blue-400 min-w-[200px] hover:shadow-2xl transition-all duration-300 transform hover:scale-105 group-hover:-rotate-1">
          <div className="flex items-center space-x-3 mb-3">
            <div className="bg-white bg-opacity-25 rounded-xl p-2 backdrop-blur-sm">
              <IconComponent className="w-5 h-5" />
            </div>
            <div className="font-semibold text-base">{data.label}</div>
          </div>
          {data.description && (
            <div className="text-xs text-blue-100 leading-relaxed font-medium">
              {data.description}
            </div>
          )}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-20 transition-opacity duration-300 rounded-xl"></div>
        </div>
      </div>
    );
  };

  const DecisionNode = ({ data }) => {
    const IconComponent = data.icon || DocumentTextIcon;
    return (
      <div className="relative">
        <Handle type="target" position={Position.Top} className="w-3 h-3" />
        <Handle type="source" position={Position.Bottom} className="w-3 h-3" />
        <Handle type="source" position={Position.Left} className="w-3 h-3" />
        <Handle type="source" position={Position.Right} className="w-3 h-3" />
        <div className="px-5 py-3 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-lg shadow-lg border-2 border-yellow-400 min-w-[180px] hover:shadow-xl transition-all duration-200 transform hover:scale-105">
          <div className="flex items-center space-x-2 mb-2">
            <div className="bg-white bg-opacity-20 rounded-lg p-1.5">
              <IconComponent className="w-4 h-4" />
            </div>
            <div className="font-semibold text-base">{data.label}</div>
          </div>
          {data.description && (
            <div className="text-xs text-yellow-100 leading-relaxed">
              {data.description}
            </div>
          )}
        </div>
      </div>
    );
  };

  const EndNode = ({ data }) => {
    const IconComponent = data.icon || TrophyIcon;
    return (
      <div className="relative group">
        <Handle type="target" position={Position.Top} className="w-3 h-3" />
        <div className="px-6 py-4 bg-gradient-to-br from-purple-500 via-pink-500 to-rose-500 text-white rounded-2xl shadow-xl border-2 border-purple-400 min-w-[220px] hover:shadow-2xl transition-all duration-300 transform hover:scale-105 group-hover:rotate-1">
          <div className="flex items-center space-x-3 mb-3">
            <div className="bg-white bg-opacity-25 rounded-xl p-2.5 backdrop-blur-sm">
              <IconComponent className="w-6 h-6" />
            </div>
            <div className="font-bold text-lg">{data.label}</div>
            <SparklesIcon className="w-5 h-5 text-purple-200 animate-bounce" />
          </div>
          {data.description && (
            <div className="text-sm text-purple-100 leading-relaxed font-medium">
              {data.description}
            </div>
          )}
          {/* Celebration particles */}
          <div className="absolute -top-2 -left-2 w-2 h-2 bg-yellow-400 rounded-full animate-ping"></div>
          <div className="absolute -top-1 -right-3 w-2 h-2 bg-pink-400 rounded-full animate-pulse"></div>
          <div className="absolute -bottom-2 -left-1 w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce"></div>
          <div className="absolute -bottom-1 -right-2 w-1.5 h-1.5 bg-green-400 rounded-full animate-ping"></div>
        </div>
      </div>
    );
  };

  const CustomNode = ({ data }) => {
    return (
      <div className="px-4 py-2 shadow-md rounded-md bg-white border-2 border-gray-200">
        <div className="font-bold text-sm">{data.label}</div>
        {data.description && (
          <div className="text-xs text-gray-500 mt-1">{data.description}</div>
        )}
      </div>
    );
  };

  const nodeTypes = {
    default: CustomNode,
    startNode: StartNode,
    processNode: ProcessNode,
    decisionNode: DecisionNode,
    endNode: EndNode,
    input: CustomNode,
    output: CustomNode,
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Enhanced Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-700 text-white p-6 shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white bg-opacity-20 rounded-xl flex items-center justify-center">
              <ChartBarIcon className="w-7 h-7" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">
                Financial Planning Flowchart Generator
              </h2>
              <p className="text-blue-100 mt-1">
                Create personalized financial planning workflows with AI-powered
                insights
              </p>
            </div>
          </div>
          {nodes.length > 0 && (
            <button
              onClick={clearFlowchart}
              className="px-4 py-2 bg-white bg-opacity-20 text-white hover:bg-opacity-30 rounded-lg transition-all duration-200 flex items-center space-x-2 backdrop-blur-sm"
            >
              <ArrowPathIcon className="w-4 h-4" />
              <span>Clear All</span>
            </button>
          )}
        </div>
      </div>

      {/* Enhanced Form */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        {/* Toggle Button for Form - Only show when flowchart exists */}
        {(isFormCollapsed || nodes.length > 0) && (
          <div
            className={`flex justify-between items-center p-4 border-b border-gray-100 ${
              isFormCollapsed
                ? "bg-gradient-to-r from-blue-50 to-purple-50"
                : "bg-white"
            } transition-all duration-300`}
          >
            <div className="flex items-center space-x-3">
              <div
                className={`w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center ${
                  isFormCollapsed ? "animate-pulse" : ""
                }`}
              >
                <ChartBarIcon className="w-4 h-4 text-white" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-900">
                  {isGenerating
                    ? "Generating Financial Plan..."
                    : "Financial Planning Form"}
                </h3>
                <p className="text-xs text-gray-600">
                  {formData.financial_goal
                    ? `Goal: ${formData.financial_goal.slice(0, 50)}${
                        formData.financial_goal.length > 50 ? "..." : ""
                      }`
                    : "Configure your financial planning parameters"}
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setIsFormCollapsed(!isFormCollapsed)}
              className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-white hover:shadow-md rounded-lg transition-all duration-200 border border-transparent hover:border-gray-200"
              disabled={isGenerating}
            >
              <span className="font-medium">
                {isFormCollapsed ? "Show Form" : "Hide Form"}
              </span>
              <div
                className={`transform transition-transform duration-200 ${
                  isFormCollapsed ? "rotate-0" : "rotate-180"
                }`}
              >
                <ChevronDownIcon className="w-4 h-4" />
              </div>
            </button>
          </div>
        )}

        {/* Collapsible Form Content */}
        <div
          className={`transition-all duration-500 ease-in-out overflow-hidden ${
            isFormCollapsed ? "max-h-0 opacity-0" : "max-h-[800px] opacity-100"
          }`}
        >
          <div className="p-6">
            <form onSubmit={generateFlowchart} className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-1">
                  <label className="block text-sm font-semibold text-gray-800 mb-3">
                    🎯 Financial Goal *
                  </label>
                  <textarea
                    name="financial_goal"
                    value={formData.financial_goal}
                    onChange={handleInputChange}
                    placeholder="e.g., Save $50,000 for a house down payment, Build retirement fund, Start emergency savings..."
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all duration-200 hover:border-gray-300"
                    rows="4"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-3">
                    ⏱️ Time Horizon
                  </label>
                  <select
                    name="time_horizon"
                    value={formData.time_horizon}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-300 bg-white"
                  >
                    <option value="3 months">🏃‍♂️ 3 months (Short term)</option>
                    <option value="6 months">🚶‍♂️ 6 months (Quick wins)</option>
                    <option value="1 year">📅 1 year (Annual goal)</option>
                    <option value="2 years">🎯 2 years (Medium term)</option>
                    <option value="5 years">🌱 5 years (Long term)</option>
                    <option value="10 years">🌳 10 years (Life goals)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-3">
                    📊 Risk Tolerance
                  </label>
                  <select
                    name="risk_tolerance"
                    value={formData.risk_tolerance}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-300 bg-white"
                  >
                    <option value="conservative">
                      🛡️ Conservative (Low risk)
                    </option>
                    <option value="moderate">⚖️ Moderate (Balanced)</option>
                    <option value="aggressive">
                      🚀 Aggressive (High growth)
                    </option>
                  </select>
                </div>
              </div>

              <div className="flex justify-center pt-4">
                <button
                  type="submit"
                  disabled={isGenerating || !formData.financial_goal.trim()}
                  className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-4 focus:ring-blue-300 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-3 shadow-lg hover:shadow-xl transform hover:scale-105"
                >
                  {isGenerating ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Generating Flowchart...</span>
                    </>
                  ) : (
                    <>
                      <ChartBarIcon className="w-5 h-5" />
                      <span>Generate Financial Plan</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isGenerating && (
        <div className="flex-1 flex items-center justify-center">
          <LoadingSpinner message="AI is creating your financial planning workflow..." />
        </div>
      )}

      {/* Enhanced Flowchart with Animations */}
      {!isGenerating && nodes.length > 0 && (
        <div className="flex-1 relative bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            connectionLineType={ConnectionLineType.SmoothStep}
            fitView
            fitViewOptions={{ padding: 0.2, maxZoom: 1.2 }}
            defaultViewport={{ x: 0, y: 0, zoom: 0.85 }}
            minZoom={0.3}
            maxZoom={2.5}
            nodesDraggable={true}
            nodesConnectable={false}
            elementsSelectable={true}
            className="rounded-lg"
            style={{
              background:
                "linear-gradient(135deg, #f8fafc 0%, #e0f2fe 50%, #f3e8ff 100%)",
            }}
          >
            <Background
              variant="dots"
              gap={30}
              size={2}
              color="#cbd5e1"
              className="opacity-60"
            />
            <Controls
              className="bg-white shadow-xl rounded-xl border border-gray-200 backdrop-blur-sm bg-opacity-90"
              showInteractive={false}
              position="bottom-right"
            />
            <MiniMap
              className="bg-white border border-gray-200 rounded-xl shadow-xl backdrop-blur-sm bg-opacity-90"
              nodeColor={(node) => {
                switch (node.type) {
                  case "startNode":
                    return "#10b981";
                  case "processNode":
                    return "#3b82f6";
                  case "decisionNode":
                    return "#f59e0b";
                  case "endNode":
                    return "#8b5cf6";
                  default:
                    return "#6b7280";
                }
              }}
              nodeStrokeWidth={3}
              maskColor="rgba(0, 0, 0, 0.05)"
              zoomable
              pannable
            />

            {/* Floating Action Panel */}
            <Panel
              position="top-left"
              className="bg-white rounded-xl shadow-lg border border-gray-200 p-4 backdrop-blur-sm bg-opacity-90"
            >
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <ChartBarIcon className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-gray-900">
                    Financial Plan
                  </h3>
                  <p className="text-xs text-gray-600">
                    {formData.time_horizon} • {formData.risk_tolerance}
                  </p>
                </div>
              </div>
            </Panel>
          </ReactFlow>

          {/* Toggle Button for Plan Details */}
          {generatedPlan && (
            <button
              onClick={() => setShowPlanDetails(!showPlanDetails)}
              className="absolute bottom-6 left-6 w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105 flex items-center justify-center"
              title={
                showPlanDetails ? "Hide plan details" : "Show plan details"
              }
            >
              <DocumentTextIcon className="w-5 h-5" />
            </button>
          )}

          {/* Quick Form Toggle Button */}
          {isFormCollapsed && (
            <button
              onClick={() => setIsFormCollapsed(false)}
              className="absolute bottom-6 right-6 w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105 flex items-center justify-center"
              title="Show form to modify parameters"
            >
              <CogIcon className="w-5 h-5" />
            </button>
          )}

          {/* Collapsible Plan Details Panel */}
          {generatedPlan && showPlanDetails && (
            <div className="absolute bottom-6 left-20 w-80 bg-white rounded-xl border border-gray-200 shadow-2xl backdrop-blur-sm bg-opacity-95 animate-in slide-in-from-left-2 duration-200">
              <div className="flex items-center justify-between p-4 border-b border-gray-100">
                <div className="flex items-center space-x-2">
                  <div className="w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                    <DocumentTextIcon className="w-3 h-3 text-white" />
                  </div>
                  <h3 className="text-sm font-semibold text-gray-900">
                    AI Plan Details
                  </h3>
                </div>
                <button
                  onClick={() => setShowPlanDetails(false)}
                  className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Close panel"
                >
                  <svg
                    className="w-4 h-4 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
              <div className="p-4 max-h-32 overflow-y-auto">
                <p className="text-xs text-gray-700 leading-relaxed">
                  {generatedPlan}
                </p>
              </div>
            </div>
          )}

          {/* Compact Legend */}
          <div className="absolute top-4 right-4 bg-white rounded-lg p-3 border border-gray-200 shadow-lg">
            <h4 className="text-xs font-medium text-gray-900 mb-2">Legend</h4>
            <div className="space-y-1.5">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-gradient-to-r from-green-500 to-green-600 rounded"></div>
                <span className="text-xs text-gray-600">Start/Goal</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-gradient-to-r from-blue-500 to-blue-600 rounded"></div>
                <span className="text-xs text-gray-600">Process</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-gradient-to-r from-yellow-500 to-orange-500 rounded"></div>
                <span className="text-xs text-gray-600">Decision</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-gradient-to-r from-purple-500 to-purple-600 rounded"></div>
                <span className="text-xs text-gray-600">Achievement</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Empty State */}
      {!isGenerating && nodes.length === 0 && (
        <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
          <div className="text-center max-w-md mx-auto px-6">
            <div className="relative mb-8">
              <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4 shadow-2xl">
                <ChartBarIcon className="w-12 h-12 text-white" />
              </div>
              {/* Floating icons around the main icon */}
              <div className="absolute -top-2 -right-2 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center animate-bounce">
                <BanknotesIcon className="w-4 h-4 text-white" />
              </div>
              <div className="absolute -bottom-2 -left-2 w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center animate-pulse">
                <ClockIcon className="w-4 h-4 text-white" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-3">
              Create Your Financial Plan
            </h3>
            <p className="text-gray-600 mb-6 leading-relaxed">
              Enter your financial goal and preferences above to generate a
              personalized, interactive planning workflow with AI-powered
              insights.
            </p>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
                <div className="text-blue-600 font-medium">✨ AI-Powered</div>
                <div className="text-gray-500">Smart recommendations</div>
              </div>
              <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
                <div className="text-green-600 font-medium">
                  🎯 Personalized
                </div>
                <div className="text-gray-500">Tailored to your goals</div>
              </div>
              <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
                <div className="text-purple-600 font-medium">
                  📊 Interactive
                </div>
                <div className="text-gray-500">Visual flowcharts</div>
              </div>
              <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
                <div className="text-orange-600 font-medium">🔄 Adaptive</div>
                <div className="text-gray-500">Adjustable strategies</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FlowchartGenerator;
