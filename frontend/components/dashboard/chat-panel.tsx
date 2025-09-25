"use client";

import { CopilotChat } from "@copilotkit/react-ui";
import { useState, useEffect } from "react";

interface ChatPanelProps {
  welcomePrompt: string;
}

export default function ChatPanel({ welcomePrompt }: ChatPanelProps) {
  const [isChatMounted, setIsChatMounted] = useState(false);

  useEffect(() => {
    setIsChatMounted(true);
  }, []);

  return (
    <div className="w-96 border-l border-gray-200 bg-white flex flex-col">
      {/* Chat Header */}
      <div className="h-16 border-b border-gray-200 flex items-center justify-center px-4 flex-shrink-0 bg-gray-50">
        <h2 className="text-lg font-semibold text-gray-900">AI Assistant</h2>
      </div>

      {/* Chat Content */}
      <div className="flex-1 overflow-y-auto relative">
        {!isChatMounted && (
          <div className="absolute inset-0 flex flex-col justify-center items-center bg-white z-10">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
            <p className="mt-2 text-gray-600">Loading chat...</p>
          </div>
        )}
        <div
          className={`h-full transition-opacity duration-200 ${
            isChatMounted ? "opacity-100" : "opacity-0"
          }`}
        >
          <CopilotChat
            labels={{
              initial: welcomePrompt,
              title: "Task Manager Assistant",
              placeholder: "Ask me to create, view, or manage your tasks!",
              stopGenerating: "Stop",
              regenerateResponse: "Regenerate",
            }}
            className="h-full"
          />
        </div>
      </div>
    </div>
  );
}
