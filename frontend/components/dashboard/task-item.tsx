import { Task } from "@/types/agent";

interface TaskItemProps {
  task: Task;
}

export default function TaskItem({ task }: TaskItemProps) {
  return (
    <div className="px-6 py-4 hover:bg-gray-50 transition-colors">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <h3 className="text-lg font-medium text-gray-900 mb-1">
            {task.title}
          </h3>
          <div className="flex items-center space-x-4 text-sm text-gray-500">
            <span>📅 {new Date(task.date).toLocaleDateString()}</span>
            <span
              className={`px-2 py-1 rounded-full text-xs font-medium ${
                task.priority === "high"
                  ? "bg-red-100 text-red-800"
                  : task.priority === "medium"
                  ? "bg-yellow-100 text-yellow-800"
                  : "bg-green-100 text-green-800"
              }`}
            >
              {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}{" "}
              Priority
            </span>
            <span
              className={`px-2 py-1 rounded-full text-xs font-medium ${
                task.status === "completed"
                  ? "bg-green-100 text-green-800"
                  : task.status === "in-progress"
                  ? "bg-blue-100 text-blue-800"
                  : "bg-gray-100 text-gray-800"
              }`}
            >
              {task.status.charAt(0).toUpperCase() + task.status.slice(1)}
            </span>
          </div>
        </div>
        <div className="text-right text-xs text-gray-400">
          <div>Created: {new Date(task.created_at).toLocaleDateString()}</div>
          <div>Updated: {new Date(task.updated_at).toLocaleDateString()}</div>
        </div>
      </div>
    </div>
  );
}
