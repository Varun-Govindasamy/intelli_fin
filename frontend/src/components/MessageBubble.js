import React from "react";
import { UserIcon, SparklesIcon } from "@heroicons/react/24/outline";

const MessageBubble = ({ message }) => {
  const isUser = message.type === "user";
  const timestamp = new Date(message.timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-6 ${
        !isUser ? "animate-fade-in" : ""
      }`}
    >
      <div
        className={`flex max-w-4xl ${
          isUser ? "flex-row-reverse" : "flex-row"
        } items-start space-x-3`}
      >
        {/* Avatar */}
        <div
          className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
            isUser
              ? "bg-primary-600 ml-3"
              : "bg-gradient-to-br from-blue-500 to-indigo-600 mr-3 shadow-md"
          }`}
        >
          {isUser ? (
            <UserIcon className="w-5 h-5 text-white" />
          ) : (
            <SparklesIcon className="w-6 h-6 text-white" />
          )}
        </div>

        {/* Message Content */}
        <div
          className={`rounded-lg px-5 py-4 shadow-sm ${
            isUser
              ? "bg-primary-600 text-white"
              : "bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 text-gray-900"
          }`}
        >
          {/* AI Response Label */}
          {!isUser && (
            <div className="flex items-center space-x-2 mb-3 pb-2 border-b border-blue-200">
              <SparklesIcon className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-semibold text-blue-700">
                AI Response
              </span>
            </div>
          )}

          <div className={`prose max-w-none ${isUser ? "" : "prose-lg"}`}>
            {message.content.split("\n").map((line, index) => (
              <p
                key={index}
                className={`${index === 0 ? "mt-0" : ""} ${
                  isUser
                    ? "text-white"
                    : "text-gray-800 font-medium leading-relaxed"
                }`}
              >
                {line}
              </p>
            ))}
          </div>

          {/* Timestamp */}
          <div
            className={`text-xs mt-3 ${
              isUser ? "text-blue-100" : "text-blue-600 font-medium"
            }`}
          >
            {timestamp}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
