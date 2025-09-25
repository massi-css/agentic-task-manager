import { Task } from "@/types/agent";
import TaskItem from "./task-item";

interface TaskListProps {
  tasks: Task[];
  hasAnyActivity: boolean;
}

export default function TaskList({ tasks, hasAnyActivity }: TaskListProps) {
  if (!hasAnyActivity && tasks.length === 0) return null;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">
          Your Tasks ({tasks.length})
        </h2>
      </div>

      {tasks.length === 0 ? (
        <div className="px-6 py-8 text-center">
          <div className="text-gray-400 text-4xl mb-4">📝</div>
          <p className="text-gray-500">
            No tasks found. Create your first task using the chat assistant!
          </p>
        </div>
      ) : (
        <div className="divide-y divide-gray-200">
          {tasks.map((task) => (
            <TaskItem key={task._id} task={task} />
          ))}
        </div>
      )}
    </div>
  );
}
