import type { Metadata } from "next";
import "./globals.css";
import { CopilotKit } from "@copilotkit/react-core";
import "@copilotkit/react-ui/styles.css";

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
      <body className="antialiased" suppressHydrationWarning>
        <CopilotKit runtimeUrl="/api/copilotkit">{children}</CopilotKit>
      </body>
    </html>
  );
}
