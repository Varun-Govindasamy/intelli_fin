import React from "react";

const LoadingSpinner = ({ message = "Loading..." }) => {
  return (
    <div className="flex items-center justify-center space-x-3 p-4">
      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
      <span className="text-gray-600 text-sm">{message}</span>
    </div>
  );
};

export default LoadingSpinner;
