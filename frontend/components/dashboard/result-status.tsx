import { AgentState } from "@/types/agent";

interface ResultStatusProps {
  result: AgentState["db_result"];
}

export default function ResultStatus({ result }: ResultStatusProps) {
  if (!result) return null;

  return (
    <div
      className={`border rounded-lg p-4 mb-6 ${
        result.success
          ? "bg-green-50 border-green-200"
          : "bg-red-50 border-red-200"
      }`}
    >
      <h2 className="text-lg font-semibold mb-2">
        <span className={result.success ? "text-green-800" : "text-red-800"}>
          Operation Result
        </span>
      </h2>
      <div className="flex items-center space-x-2">
        <span className="text-lg">{result.success ? "✅" : "❌"}</span>
        <span
          className={`text-sm ${
            result.success ? "text-green-700" : "text-red-700"
          }`}
        >
          {result.message || result.error || "Operation completed"}
        </span>
      </div>
    </div>
  );
}
