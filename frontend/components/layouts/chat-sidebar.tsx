"use client";

import { CopilotChat, useCopilotChatSuggestions } from "@copilotkit/react-ui";
import { useCoAgentStateRender } from "@copilotkit/react-core";
import { suggestionPrompt } from "../../utils/prompts";
import { useState, useEffect } from "react";

function ToolLogs({ logs }: { logs: any[] }) {
  return (
    <div className="tool-logs">
      {logs.map((log, index) => (
        <div
          key={index}
          className="log-entry p-2 mb-2 bg-gray-100 rounded text-sm"
        >
          <pre>{JSON.stringify(log, null, 2)}</pre>
        </div>
      ))}
    </div>
  );
}

export default function ChatSidebar() {
  const [mounted, setMounted] = useState(false);

  useCopilotChatSuggestions({
    available: "enabled",
    instructions: suggestionPrompt,
  });

  // Add tool log renderer
  useCoAgentStateRender({
    name: "task_manager_agent",
    render: (state) => <ToolLogs logs={state?.state?.tool_logs || []} />,
  });

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="fixed left-0 top-0 h-full w-96 bg-white border-r border-gray-200 shadow-lg z-40">
        {/* Sidebar Header */}
        <div className="h-16 border-b border-gray-200 flex items-center justify-center px-4">
          <h2 className="text-lg font-semibold text-gray-900">AI Assistant</h2>
        </div>
        {/* Loading placeholder */}
        <div className="h-[calc(100vh-4rem)] flex flex-col justify-center items-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          <p className="mt-2 text-gray-600">Loading chat...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed left-0 top-0 h-full w-96 bg-white border-r border-gray-200 shadow-lg z-40">
      {/* Sidebar Header */}
      <div className="h-16 border-b border-gray-200 flex items-center justify-center px-4">
        <h2 className="text-lg font-semibold text-gray-900">AI Assistant</h2>
      </div>

      {/* Chat Content */}
      <div className="h-[calc(100vh-4rem)] flex flex-col justify-end">
        <CopilotChat
          labels={{
            initial: "Hello! How can I help you today?",
            title: "My Copilot",
            placeholder: "Ask me anything!",
            stopGenerating: "Stop",
            regenerateResponse: "Regenerate",
          }}
        />
      </div>
    </div>
  );
}
