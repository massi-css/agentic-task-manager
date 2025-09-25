import { AgentState } from "@/types/agent";

interface OperationStatusProps {
  operation: string;
  parameters?: AgentState["parameters"];
}

export default function OperationStatus({
  operation,
  parameters,
}: OperationStatusProps) {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
      <h2 className="text-lg font-semibold text-blue-800 mb-2">
        Current Operation
      </h2>
      <div className="flex items-center space-x-2">
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          {operation}
        </span>
        {parameters && (
          <span className="text-sm text-blue-600">
            {parameters.title && `Title: "${parameters.title}"`}
            {parameters.priority && ` | Priority: ${parameters.priority}`}
            {parameters.status && ` | Status: ${parameters.status}`}
          </span>
        )}
      </div>
    </div>
  );
}
