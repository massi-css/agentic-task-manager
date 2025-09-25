"use client";

import { useCoAgentStateRender } from "@copilotkit/react-core";
import { useCopilotChatSuggestions } from "@copilotkit/react-ui";
import { useState } from "react";
import { suggestionPrompt, welcomePrompt } from "@/utils/prompts";
import { AgentState } from "@/types/agent";
import DashboardContent from "@/components/dashboard/dashboard-content";
import ChatPanel from "@/components/dashboard/chat-panel";

export default function Home() {
  const [currentAgentState, setCurrentAgentState] = useState<
    AgentState | undefined
  >();

  useCopilotChatSuggestions({
    available: "enabled",
    instructions: suggestionPrompt,
  });

  useCoAgentStateRender<AgentState>({
    name: "task_manager_agent",
    render: ({ state }) => {
      setCurrentAgentState(state);
      return null; // We don't return JSX from here
    },
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex h-screen">
        {/* Main Dashboard Content */}
        <div className="flex-1 overflow-y-auto">
          <DashboardContent state={currentAgentState} />
        </div>

        {/* Chat Panel */}
        <ChatPanel welcomePrompt={welcomePrompt} />
      </div>
    </div>
  );
}
