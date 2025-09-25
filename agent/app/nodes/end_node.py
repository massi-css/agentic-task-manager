"""End node for the workflow."""

from langchain_core.runnables import RunnableConfig
from langgraph.types import Command
from langgraph.graph import END
from copilotkit.langgraph import copilotkit_emit_state

from nodes.state import TaskManagerState


async def end_node(state: TaskManagerState, config: RunnableConfig) -> Command:
    """Final node to clean up and end the workflow"""
    
    try:
        # Clear tool logs
        state["tool_logs"] = []
        await copilotkit_emit_state(config, state)
        
        return Command(goto=END, update=state)
    
    except Exception as e:
        print(f"End node cleanup failed: {str(e)}")
        # Even if cleanup fails, we should end the workflow
        # Just ensure tool_logs is at least an empty list
        if "tool_logs" not in state:
            state["tool_logs"] = []
        
        return Command(goto=END, update=state)