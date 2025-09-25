"use client";

interface TaskExamplesProps {
  onSuggestionClick?: (suggestion: string) => void;
}

export default function TaskExamples({ onSuggestionClick }: TaskExamplesProps) {
  const examples = [
    {
      title: "Add a Task",
      description: "Create a new task with priority and due date",
      example:
        "Add a high priority task 'Finish project proposal' due tomorrow",
      icon: "➕",
    },
    {
      title: "View Tasks",
      description: "Get all your tasks or filter by status/priority",
      example: "Show me all my pending tasks",
      icon: "👀",
    },
    {
      title: "Update Task",
      description: "Modify existing task details or status",
      example: "Mark 'Finish project proposal' as completed",
      icon: "✏️",
    },
    {
      title: "Delete Task",
      description: "Remove tasks you no longer need",
      example: "Delete the task about grocery shopping",
      icon: "🗑️",
    },
    {
      title: "Filter by Priority",
      description: "View tasks based on their importance",
      example: "Show me all high priority tasks",
      icon: "⚡",
    },
    {
      title: "Filter by Date",
      description: "Find tasks for specific time periods",
      example: "Show me tasks for this week",
      icon: "📅",
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        🚀 Try these commands
      </h2>
      <p className="text-gray-600 mb-6">
        Click on any example below or type similar commands in the chat to
        interact with your task manager:
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {examples.map((example, index) => (
          <div
            key={index}
            onClick={() => onSuggestionClick?.(example.example)}
            className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:bg-blue-50 cursor-pointer transition-all duration-200"
          >
            <div className="flex items-start space-x-3">
              <span className="text-2xl">{example.icon}</span>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-1">
                  {example.title}
                </h3>
                <p className="text-sm text-gray-600 mb-2">
                  {example.description}
                </p>
                <code className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-xs">
                  "{example.example}"
                </code>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
