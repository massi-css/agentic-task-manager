"use client";
import { ReactNode } from "react";
import ChatSidebar from "./chat-sidebar";

interface MainLayoutProps {
  children: ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      <div className="flex-1 flex relative">
        {/* Chat Sidebar */}
        <ChatSidebar />
        {/* Main Content */}
        <main className="flex-1 ml-96 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
