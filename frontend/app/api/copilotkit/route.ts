import { CopilotRuntime, copilotRuntimeNextJSAppRouterEndpoint, GoogleGenerativeAIAdapter } from "@copilotkit/runtime";
import { NextRequest } from "next/server";

const serviceAdapter = new GoogleGenerativeAIAdapter();
const runtime = new CopilotRuntime({
  remoteEndpoints: [{ url: process.env.NEXT_PUBLIC_LANGGRAPH_URL || "http://localhost:8000/copilotkit" }],
});

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });
  return handleRequest(req);
};
