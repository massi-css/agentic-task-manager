import type { Metadata } from "next";
import "./globals.css";
import { CopilotKit } from "@copilotkit/react-core";

export const metadata: Metadata = {
  title: "Agentic Task Manager",
  description: "Manage your tasks with AI agent seamlessly.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <CopilotKit runtimeUrl="/api/copilotkit">{children}</CopilotKit>
      </body>
    </html>
  );
}
