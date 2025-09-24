"use client";
import { CopilotChat, useCopilotChatSuggestions } from "@copilotkit/react-ui";
import { suggestionPrompt } from "../../utils/prompts";

export default function ChatSidebar() {
  // Enable chat suggestions
  useCopilotChatSuggestions({
    available: "enabled",
    instructions: suggestionPrompt,
  });

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
