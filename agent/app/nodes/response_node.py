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
        
        # Generate fallback response instead of raising exception
        db_result = state.get("db_result", {})
        operation = state.get("operation", "UNKNOWN")
        
        # Create a fallback response based on available information
        if db_result.get("success") is False:
            fallback_response = f"I encountered an issue while processing your request: {db_result.get('message', 'Unknown error occurred')}"
        else:
            fallback_response = f"I processed your {operation.lower().replace('_', ' ')} request, but had trouble generating a detailed response. The operation may have completed successfully."
        
        state["final_response"] = fallback_response
        
        # Update log
        state["tool_logs"][-1]["status"] = "failed"
        state["tool_logs"][-1]["message"] = f"Response generation failed, using fallback: {str(e)}"
        await copilotkit_emit_state(config, state)
        
        # Add AI message to conversation with fallback response
        ai_message = AIMessage(content=fallback_response)
        state["messages"].append(ai_message)
        
        # Continue to end node instead of raising error
        print("Continuing workflow with fallback response after response generation failure")
        return Command(goto="end_node", update=state)