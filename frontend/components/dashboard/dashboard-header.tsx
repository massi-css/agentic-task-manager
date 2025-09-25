interface DashboardHeaderProps {
  hasAnyActivity: boolean;
}

export default function DashboardHeader({
  hasAnyActivity,
}: DashboardHeaderProps) {
  return (
    <div className="mb-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">
        Task Manager Dashboard
      </h1>
      <p className="text-gray-600">
        Manage your tasks with AI assistance.{" "}
        {hasAnyActivity
          ? "Current status and operations are displayed below."
          : "Start by creating your first task using the AI chat assistant."}
      </p>
    </div>
  );
}
