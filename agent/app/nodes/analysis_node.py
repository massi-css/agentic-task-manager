"""Task analysis node for the workflow."""

import sys
import os
import uuid
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from copilotkit.langgraph import copilotkit_emit_state

# Add the app directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from nodes.state import TaskManagerState
from utils.llm_model import get_llm_model
from utils.prompts import TASK_ANALYSIS_PROMPT
from utils.json_parser import parse_json_response


async def task_analysis_node(state: TaskManagerState, config: RunnableConfig) -> Command:
    """Analyze user request to determine task operation and extract parameters"""
    if "tool_logs" not in state:
        state["tool_logs"] = []
    if "operation" not in state:
        state["operation"] = None
    if "parameters" not in state:
        state["parameters"] = None
    if "db_result" not in state:
        state["db_result"] = None
    if "retry_count" not in state:
        state["retry_count"] = 0
    
    # Add log entry
    state["tool_logs"].append({
        "id": str(uuid.uuid4()),
        "message": "Analyzing your request...",
        "status": "processing"
    })
    print("analyzing user request...")
    await copilotkit_emit_state(config, state)
    
    try:
        # Get the user message
        user_message = state["messages"][-1].content if state["messages"] else ""
        print("user message:", user_message)
        
        print("initiating LLM analysis...")
        
        # Use LLM to analyze the request
        model = get_llm_model(temperature=0.1)
        print("llm model initialized")
        
        analysis_prompt = f"{TASK_ANALYSIS_PROMPT}\n\nUser message: {user_message}"
        print("analysis prompt prepared")
        
        response = await model.ainvoke([HumanMessage(content=analysis_prompt)], config)
        print("LLM analysis response:", response.content)
        
        # Parse the JSON response
        analysis = parse_json_response(response.content)
        operation = analysis.get("operation")
        parameters = analysis.get("parameters", {})
        
        # Update state
        state["operation"] = operation
        state["parameters"] = parameters
        
        # Update log
        state["tool_logs"][-1]["status"] = "completed"
        state["tool_logs"][-1]["message"] = "Request analyzed"
        print("completed analysis")
        await copilotkit_emit_state(config, state)
        
        return Command(goto="database_operation_node", update=state)
        
    except Exception as e:
        print(f"Task analysis failed: {str(e)}")
        
        # Set default values to allow workflow to continue
        state["operation"] = "UNKNOWN"
        state["parameters"] = {"error_message": str(e)}
        
        # Update log
        state["tool_logs"][-1]["status"] = "failed"
        state["tool_logs"][-1]["message"] = f"Analysis failed: {str(e)}"
        await copilotkit_emit_state(config, state)
        
        # Continue to next node instead of raising error
        print("Continuing workflow with default values after analysis failure")
        return Command(goto="database_operation_node", update=state)