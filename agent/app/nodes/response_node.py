"""Response generation node for the workflow."""

import uuid
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from langgraph.types import Command
from copilotkit.langgraph import copilotkit_emit_state

from nodes.state import TaskManagerState
from utils.response_helpers import generate_task_summary_response, generate_standard_response


async def response_generation_node(state: TaskManagerState, config: RunnableConfig) -> Command:
    """Generate natural language response based on operation result"""
    
    # Add log entry
    state["tool_logs"].append({
        "id": str(uuid.uuid4()),
        "message": "Generating response...",
        "status": "processing"
    })
    await copilotkit_emit_state(config, state)
    
    try:
        result = state["db_result"]
        operation = state["operation"]
        
        if operation == "SUMMARIZE_TASKS" and result.get("success"):
            # Use special summarization prompt for task summaries
            summary_data = result.get("summary", {})
            response = await generate_task_summary_response(summary_data, config)
        else:
            # Generate standard response
            response = await generate_standard_response(operation, result, config)
        
        state["final_response"] = response
        
        # Update log
        state["tool_logs"][-1]["status"] = "completed"
        state["tool_logs"][-1]["message"] = "Response generated"
        print("completed")
        print("response generated")
        await copilotkit_emit_state(config, state)
        
        # Add AI message to conversation
        ai_message = AIMessage(content=response)
        state["messages"].append(ai_message)
        return Command(goto="end_node", update=state)
        
    except Exception as e:
        print(f"Response generation failed: {str(e)}")
        state["tool_logs"][-1]["status"] = "failed"
        state["tool_logs"][-1]["message"] = f"Response generation failed: {str(e)}"
        await copilotkit_emit_state(config, state)
        raise e