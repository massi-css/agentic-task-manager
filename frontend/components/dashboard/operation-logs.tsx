import { ToolLog } from "@/types/agent";

interface OperationLogsProps {
  logs: ToolLog[];
}

export default function OperationLogs({ logs }: OperationLogsProps) {
  if (logs.length === 0) return null;

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-3">
        Operation Logs
      </h2>
      <div className="space-y-2">
        {logs.map((log) => (
          <div key={log.id} className="flex items-center space-x-2">
            <span className="text-lg">
              {log.status === "processing"
                ? "⏳"
                : log.status === "completed"
                ? "✅"
                : log.status === "error"
                ? "❌"
                : "📝"}
            </span>
            <span className="text-sm text-gray-700">{log.message}</span>
            {log.status === "processing" && (
              <span className="text-xs text-gray-500">...</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
