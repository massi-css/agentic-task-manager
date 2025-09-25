"use client";

interface AgentStatusIndicatorProps {
  operation?: string;
  isProcessing?: boolean;
  hasError?: boolean;
}

export default function AgentStatusIndicator({
  operation,
  isProcessing,
  hasError,
}: AgentStatusIndicatorProps) {
  if (!operation && !isProcessing && !hasError) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 z-50">
      <div
        className={`
        flex items-center space-x-2 px-4 py-2 rounded-lg shadow-lg border
        ${
          hasError
            ? "bg-red-50 border-red-200 text-red-800"
            : isProcessing
            ? "bg-blue-50 border-blue-200 text-blue-800"
            : "bg-green-50 border-green-200 text-green-800"
        }
      `}
      >
        {isProcessing && (
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current" />
        )}
        <span className="text-lg">
          {hasError ? "❌" : isProcessing ? "⏳" : "✅"}
        </span>
        <span className="text-sm font-medium">
          {hasError
            ? "Operation Failed"
            : isProcessing
            ? `Processing: ${operation || "Unknown"}`
            : "Operation Complete"}
        </span>
      </div>
    </div>
  );
}
