import { AgentState } from "@/types/agent";
import DashboardHeader from "./dashboard-header";
import OperationStatus from "./operation-status";
import OperationLogs from "./operation-logs";
import ResultStatus from "./result-status";
import TaskList from "./task-list";
import TaskExamples from "@/components/dashboard/task-examples";

interface DashboardContentProps {
  state?: AgentState;
}

export default function DashboardContent({ state }: DashboardContentProps) {
  const tasks = state?.db_result?.tasks || [];
  const currentOperation = state?.operation;
  const toolLogs = state?.tool_logs || [];
  const dbResult = state?.db_result;
  const hasAnyActivity = Boolean(
    currentOperation || toolLogs.length > 0 || dbResult
  );

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <DashboardHeader hasAnyActivity={hasAnyActivity} />

      {/* Show examples only when no activity */}
      {!hasAnyActivity && tasks.length === 0 && <TaskExamples />}

      {/* Current Operation */}
      {currentOperation && (
        <OperationStatus
          operation={currentOperation}
          parameters={state?.parameters}
        />
      )}

      {/* Operation Logs */}
      <OperationLogs logs={toolLogs} />

      {/* Database Result Status */}
      <ResultStatus result={dbResult} />

      {/* Tasks Display */}
      <TaskList tasks={tasks} hasAnyActivity={hasAnyActivity} />
    </div>
  );
}
