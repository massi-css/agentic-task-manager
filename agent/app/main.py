from fastapi import FastAPI
import uvicorn
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitSDK, LangGraphAgent
from workflow import task_manager_graph
import os

app = FastAPI()

sdk = CopilotKitSDK(
    agents=[
        LangGraphAgent(
            name="task_manager_agent",
            description="An agent that can help with task management.",
            graph=task_manager_graph,
        ),
    ]
)

add_fastapi_endpoint(app, sdk, "/copilotkit")

# just a simple health check endpoint
@app.get("/healthz")
def health():
    return {"status": "ok"}

def main():
    """Run the uvicorn server."""
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "main:app",
        port=port,
        reload=True,
    )

if __name__ == "__main__":
    main()