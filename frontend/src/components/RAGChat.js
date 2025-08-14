import React, { useState, useRef, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import {
  PaperAirplaneIcon,
  DocumentTextIcon,
  CloudArrowUpIcon,
  TrashIcon,
  ChevronUpIcon,
  ChevronDownIcon,
} from "@heroicons/react/24/outline";
import { apiService } from "../services/api";
import toast from "react-hot-toast";
import MessageBubble from "./MessageBubble";
import LoadingSpinner from "./LoadingSpinner";

const RAGChat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: "assistant",
      content:
        "Welcome to the Document Analysis section! Upload PDF financial reports and I'll help you analyze them. You can ask questions about the content, get summaries, or extract specific information.",
      timestamp: new Date().toISOString(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isUploadAreaCollapsed, setIsUploadAreaCollapsed] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const onDrop = async (acceptedFiles) => {
    const pdfFiles = acceptedFiles.filter(
      (file) => file.type === "application/pdf"
    );

    if (pdfFiles.length === 0) {
      toast.error("Please upload only PDF files");
      return;
    }

    if (pdfFiles.length > 5) {
      toast.error("Maximum 5 files allowed at once");
      return;
    }

    setIsUploading(true);

    try {
      const response = await apiService.uploadDocuments(pdfFiles);

      const newFiles = pdfFiles.map((file) => ({
        name: file.name,
        size: file.size,
        uploadedAt: new Date().toISOString(),
      }));

      setUploadedFiles((prev) => [...prev, ...newFiles]);

      const uploadMessage = {
        id: Date.now(),
        type: "assistant",
        content: `Successfully uploaded and processed ${
          pdfFiles.length
        } document(s): ${pdfFiles
          .map((f) => f.name)
          .join(", ")}. You can now ask questions about the content.`,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, uploadMessage]);
      toast.success(response.message || "Documents uploaded successfully");
    } catch (error) {
      console.error("Error uploading documents:", error);
      toast.error("Failed to upload documents. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
    },
    maxFiles: 5,
    disabled: isUploading,
  });

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!inputMessage.trim() || isLoading) return;

    if (uploadedFiles.length === 0) {
      toast.error("Please upload some PDF documents first");
      return;
    }

    const userMessage = {
      id: Date.now(),
      type: "user",
      content: inputMessage.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    // Collapse the upload area when AI starts generating
    setIsUploadAreaCollapsed(true);

    try {
      const response = await apiService.queryRAG(userMessage.content);

      const assistantMessage = {
        id: Date.now() + 1,
        type: "assistant",
        content: response.response,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error querying documents:", error);
      toast.error("Failed to query documents. Please try again.");

      const errorMessage = {
        id: Date.now() + 1,
        type: "assistant",
        content:
          "I apologize, but I'm having trouble accessing the uploaded documents. Please try again.",
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 1,
        type: "assistant",
        content:
          "Chat cleared! You can continue asking questions about your uploaded documents.",
        timestamp: new Date().toISOString(),
      },
    ]);
  };

  const removeFile = (fileName) => {
    setUploadedFiles((prev) => prev.filter((file) => file.name !== fileName));
    toast.success("File removed from list");
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const suggestedQuestions = [
    "Summarize the key financial metrics from the uploaded reports",
    "What are the main risks mentioned in the documents?",
    "Compare the revenue growth across different periods",
    "What are the company's future outlook and projections?",
    "Identify any significant changes in financial position",
  ];

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              Document Analysis & RAG
            </h2>
            <p className="text-sm text-gray-600">
              Upload financial PDFs and get AI-powered insights
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <span className="text-sm text-gray-600">
              {uploadedFiles.length} document(s) uploaded
            </span>
            <button
              onClick={() => setIsUploadAreaCollapsed(!isUploadAreaCollapsed)}
              className="flex items-center space-x-1 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              title={
                isUploadAreaCollapsed ? "Show Upload Area" : "Hide Upload Area"
              }
            >
              {isUploadAreaCollapsed ? (
                <>
                  <ChevronDownIcon className="w-4 h-4" />
                  <span>Show Upload</span>
                </>
              ) : (
                <>
                  <ChevronUpIcon className="w-4 h-4" />
                  <span>Hide Upload</span>
                </>
              )}
            </button>
            <button
              onClick={clearChat}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Clear Chat
            </button>
          </div>
        </div>
      </div>

      {/* File Upload Area - Collapsible */}
      {isUploadAreaCollapsed && uploadedFiles.length > 0 && (
        <div className="bg-blue-50 border-b border-blue-200 px-4 py-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-sm text-blue-700">
              <DocumentTextIcon className="w-4 h-4" />
              <span>{uploadedFiles.length} document(s) ready for analysis</span>
            </div>
            <button
              onClick={() => setIsUploadAreaCollapsed(false)}
              className="text-xs text-blue-600 hover:text-blue-800 underline"
            >
              Show files
            </button>
          </div>
        </div>
      )}

      <div
        className={`bg-white border-b border-gray-200 transition-all duration-500 ease-in-out overflow-hidden ${
          isUploadAreaCollapsed ? "max-h-0 border-b-0" : "max-h-96"
        }`}
      >
        <div className="p-4 space-y-4">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer ${
              isDragActive
                ? "border-primary-400 bg-primary-50"
                : "border-gray-300 hover:border-gray-400 hover:bg-gray-50"
            } ${isUploading ? "opacity-50 cursor-not-allowed" : ""}`}
          >
            <input {...getInputProps()} />
            <CloudArrowUpIcon className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            {isUploading ? (
              <div className="space-y-2">
                <LoadingSpinner message="Uploading and processing documents..." />
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-gray-600">
                  {isDragActive
                    ? "Drop the PDF files here..."
                    : "Drag & drop PDF files here, or click to select"}
                </p>
                <p className="text-sm text-gray-500">
                  Maximum 5 files, PDF format only
                </p>
              </div>
            )}
          </div>

          {/* Uploaded Files List */}
          {uploadedFiles.length > 0 && (
            <div className="mt-4">
              <h3 className="text-sm font-medium text-gray-900 mb-2">
                Uploaded Documents
              </h3>
              <div className="space-y-2">
                {uploadedFiles.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      <DocumentTextIcon className="w-5 h-5 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {file.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {formatFileSize(file.size)} •{" "}
                          {new Date(file.uploadedAt).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(file.name)}
                      className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gradient-to-b from-gray-50 to-white">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {isLoading && (
          <div className="flex justify-center">
            <LoadingSpinner message="Analyzing documents..." />
          </div>
        )}

        {/* Suggested Questions */}
        {uploadedFiles.length > 0 && messages.length === 1 && !isLoading && (
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <h3 className="text-sm font-medium text-gray-900 mb-3">
              Suggested Questions
            </h3>
            <div className="space-y-2">
              {suggestedQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => setInputMessage(question)}
                  className="w-full text-left p-3 text-sm text-gray-700 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 p-4">
        <form onSubmit={handleSendMessage} className="flex space-x-3">
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                uploadedFiles.length === 0
                  ? "Upload PDF documents first, then ask questions about them..."
                  : "Ask questions about your uploaded documents..."
              }
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
              rows="2"
              disabled={isLoading || uploadedFiles.length === 0}
            />
          </div>
          <button
            type="submit"
            disabled={
              !inputMessage.trim() || isLoading || uploadedFiles.length === 0
            }
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <PaperAirplaneIcon className="w-5 h-5" />
          </button>
        </form>

        <div className="mt-2 text-xs text-gray-500 text-center">
          {uploadedFiles.length === 0
            ? "Upload PDF documents to start analyzing"
            : "Press Enter to send, Shift+Enter for new line"}
        </div>
      </div>
    </div>
  );
};

export default RAGChat;
