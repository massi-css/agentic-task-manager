"use client";

import { CopilotChat, useCopilotChatSuggestions } from "@copilotkit/react-ui";
import { useCoAgentStateRender } from "@copilotkit/react-core";
import { suggestionPrompt, welcomePrompt } from "../../utils/prompts";
import { useState, useEffect, useRef } from "react";

function ToolLogs({ logs }: { logs: any[] }) {
  return (
    <div className="tool-logs">
      {logs.map((log, index) => (
        <div
          key={index}
          className="log-entry p-2 mb-2 bg-gray-100 rounded text-sm flex gap-2"
        >
          {log.status === "processing" && (
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
          )}
          <span>{log.message}</span>
        </div>
      ))}
    </div>
  );
}

export default function ChatSidebar() {
  const [isMounted, setIsMounted] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);

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
    setIsMounted(true);
  }, []);

  return (
    <div className="fixed left-0 top-0 h-full w-96 bg-white border-r border-gray-200 shadow-lg z-40 flex flex-col overflow-y-auto">
      {/* Sidebar Header */}
      <div className="h-16 border-b border-gray-200 flex items-center justify-center px-4 flex-shrink-0">
        <h2 className="text-lg font-semibold text-gray-900">AI Assistant</h2>
      </div>

      {/* Chat Content */}
      <div
        ref={chatRef}
        className="flex-1 overflow-y-auto relative"
        style={{ minHeight: 0 }}
      >
        {!isMounted && (
          <div className="absolute inset-0 flex flex-col justify-center items-center bg-white z-10">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
            <p className="mt-2 text-gray-600">Loading chat...</p>
          </div>
        )}
        <div
          className={`h-full transition-opacity duration-200 ${
            isMounted ? "opacity-100" : "opacity-0"
          }`}
        >
          <CopilotChat
            labels={{
              initial: welcomePrompt,
              title: "My Copilot",
              placeholder: "Ask me anything!",
              stopGenerating: "Stop",
              // regenerateResponse: "Regenerate",
            }}
            className="h-full"
          />
        </div>
      </div>
    </div>
  );
}
