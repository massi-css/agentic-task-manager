import os
import uuid
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from copilotkit import CopilotKitState
from copilotkit.langgraph import copilotkit_emit_state
from prompts import TASK_ANALYSIS_PROMPT, TASK_EXECUTOR_PROMPT, TASK_SUMMARIZER_PROMPT
from task_database import task_db

load_dotenv()

class TaskManagerState(CopilotKitState):
    """State for the task manager agent"""
    messages: List[BaseMessage] = []
    tool_logs: List[Dict[str, Any]] = []
    operation: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    db_result: Optional[Dict[str, Any]] = None
    final_response: Optional[str] = None

async def task_analysis_node(state: TaskManagerState, config: RunnableConfig) -> Command:
    """Analyze user request to determine task operation and extract parameters"""
    
    # log entry
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
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
        print("llm model initialized")
        
        analysis_prompt = f"{TASK_ANALYSIS_PROMPT}\n\nUser message: {user_message}"
        print("analysis prompt prepared")
        
        response = await model.ainvoke([HumanMessage(content=analysis_prompt)], config)
        print("LLM analysis response:", response.content)
        
        # Parse the JSON response (handle markdown code blocks)
        response_content = response.content.strip()
        
        # Remove markdown code block markers if present
        if response_content.startswith("```json"):
            response_content = response_content[7:]  # Remove ```json
        if response_content.startswith("```"):
            response_content = response_content[3:]   # Remove ```
        if response_content.endswith("```"):
            response_content = response_content[:-3]  # Remove trailing ```
        
        response_content = response_content.strip()
        print("Cleaned JSON content:", response_content)
        
        analysis = json.loads(response_content)
        operation = analysis.get("operation")
        parameters = analysis.get("parameters", {})
        
        # Update state
        state["operation"] = operation
        state["parameters"] = parameters
        
        # Update log
        state["tool_logs"][-1]["status"] = "completed"
        state["tool_logs"][-1]["message"] = f"Request analyzed: {operation}"
        print("completed analysis")
        print(f"Operation: {operation}, Parameters: {parameters}")
        await copilotkit_emit_state(config, state)
        
        return Command(goto="database_operation_node", update=state)
        
    except Exception as e:
        print(f" Task analysis failed: {str(e)}")
        state["tool_logs"][-1]["status"] = "failed"
        state["tool_logs"][-1]["message"] = f"Analysis failed: {str(e)}"
        await copilotkit_emit_state(config, state)
        raise e

async def database_operation_node(state: TaskManagerState, config: RunnableConfig) -> Command:
    """Execute the database operation based on the analyzed request"""
    
    operation = state["operation"]
    parameters = state["parameters"] or {}
    
    # Add log entry
    state["tool_logs"].append({
        "id": str(uuid.uuid4()),
        "message": f"Executing {operation.lower().replace('_', ' ')}...",
        "status": "processing"
    })
    print(f"executing operation: {operation}")
    await copilotkit_emit_state(config, state)
    
    try:
        # Connect to database
        await task_db.connect()
        
        # Execute operation based on type
        if operation == "ADD_TASK":
            result = await task_db.add_task(
                title=parameters.get("title", "Untitled Task"),
                date=parameters.get("date"),
                priority=parameters.get("priority", "medium"),
                status=parameters.get("status", "pending")
            )
        elif operation == "GET_TASKS":
            result = await task_db.get_tasks(
                date_range=parameters.get("date_range"),
                priority_filter=parameters.get("priority_filter"),
                status_filter=parameters.get("status_filter")
            )
        elif operation == "UPDATE_TASK":
            result = await task_db.update_task(
                task_identifier=parameters.get("task_identifier", ""),
                updates=parameters.get("updates", {})
            )
        elif operation == "DELETE_TASK":
            result = await task_db.delete_task(
                task_identifier=parameters.get("task_identifier", "")
            )
        elif operation == "MARK_DONE":
            result = await task_db.mark_done(
                task_identifier=parameters.get("task_identifier", "")
            )
        elif operation == "PRIORITIZE":
            result = await task_db.set_priority(
                task_identifier=parameters.get("task_identifier", ""),
                priority=parameters.get("priority", "medium")
            )
        elif operation == "SUMMARIZE_TASKS":
            result = await task_db.get_task_summary(
                filter_criteria=parameters.get("filter_criteria", {})
            )
        else:
            result = {
                "success": False,
                "message": f"Unknown operation: {operation}"
            }
        
        state["db_result"] = result
        
        # Update log
        if result.get("success"):
            state["tool_logs"][-1]["status"] = "completed"
            state["tool_logs"][-1]["message"] = "Operation completed successfully"
            print("operation completed successfully")
        else:
            state["tool_logs"][-1]["status"] = "failed"
            state["tool_logs"][-1]["message"] = result.get("message", "Operation failed")
            print("message:", result.get("message", "Operation failed"))
            print("operation failed")
        
        await copilotkit_emit_state(config, state)
        
        # Disconnect from database
        await task_db.disconnect()
        
        return Command(goto="response_generation_node", update=state)
        
    except Exception as e:
        print(f" Database operation failed: {str(e)}")
        state["tool_logs"][-1]["status"] = "failed"
        state["tool_logs"][-1]["message"] = f"Database operation failed: {str(e)}"
        await copilotkit_emit_state(config, state)
        
        # Set error result
        state["db_result"] = {
            "success": False,
            "message": f"Database error: {str(e)}"
        }
        
        # Ensure database is disconnected
        try:
            await task_db.disconnect()
        except Exception as disconnect_error:
            print(f"⚠️ Failed to disconnect database: {str(disconnect_error)}")
            
        raise e

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
            response = await _generate_task_summary_response(summary_data, config)
        else:
            # Generate standard response
            response = await _generate_standard_response(operation, result, config)
        
        state["final_response"] = response
        
        # Update log
        state["tool_logs"][-1]["status"] = "completed"
        state["tool_logs"][-1]["message"] = "Response generated"
        print("completed")
        print("response generated")
        await copilotkit_emit_state(config, state)
        
        # Add AI message to conversation
        ai_message = AIMessage(content=response)
        return Command(goto="end_node", update={"messages": [ai_message]})
        
    except Exception as e:
        print(f" Response generation failed: {str(e)}")
        state["tool_logs"][-1]["status"] = "failed"
        state["tool_logs"][-1]["message"] = f"Response generation failed: {str(e)}"
        await copilotkit_emit_state(config, state)
        raise e

async def end_node(state: TaskManagerState, config: RunnableConfig) -> Command:
    """Final node to clean up and end the workflow"""
    
    # Clear tool logs
    state["tool_logs"] = []
    await copilotkit_emit_state(config, state)
    
    return Command(goto=END, update=state)


async def _generate_task_summary_response(summary_data: Dict[str, Any], config: RunnableConfig) -> str:
    """Generate natural language summary of tasks"""
    try:
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.3,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
        
        summary_prompt = f"""
        {TASK_SUMMARIZER_PROMPT}
        
        Task Summary Data:
        {json.dumps(summary_data, default=str, indent=2)}
        
        Generate a helpful summary response for the user.
        """
        
        response = await model.ainvoke([HumanMessage(content=summary_prompt)], config)
        return response.content.strip()
        
    except Exception as e:
        print(f" Failed to generate task summary with LLM: {str(e)}")
        # Fallback to simple summary
        total = summary_data.get("total_tasks", 0)
        pending = summary_data.get("pending_tasks", 0)
        done = summary_data.get("done_tasks", 0)
        high_priority = summary_data.get("high_priority", 0)
        
        return f"""Here's your task summary:
        
📊 **Total Tasks:** {total}
✅ **Completed:** {done}
⏳ **Pending:** {pending}
🚨 **High Priority:** {high_priority}

{f"You have {pending} pending tasks" if pending > 0 else "All caught up! 🎉"}
{f" with {high_priority} marked as high priority." if high_priority > 0 else "."}"""

async def _generate_standard_response(operation: str, result: Dict[str, Any], config: RunnableConfig) -> str:
    """Generate standard response for non-summary operations"""
    try:
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.3,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
        
        response_prompt = f"""
        {TASK_EXECUTOR_PROMPT}
        
        Operation: {operation}
        Result: {json.dumps(result, default=str, indent=2)}
        
        Generate a natural, helpful response for the user.
        """
        
        response = await model.ainvoke([HumanMessage(content=response_prompt)], config)
        return response.content.strip()
        
    except Exception as e:
        print(f" Failed to generate standard response with LLM: {str(e)}")
        # Fallback to simple response
        if result.get("success"):
            return result.get("message", "Operation completed successfully!")
        else:
            return f"Sorry, {result.get('message', 'the operation failed')}."

def create_task_manager_workflow() -> StateGraph:
    """Create and configure the task manager workflow graph"""
    
    # Create workflow graph
    workflow = StateGraph(TaskManagerState)
    
    # Add nodes
    workflow.add_node("task_analysis_node", task_analysis_node)
    workflow.add_node("database_operation_node", database_operation_node)
    workflow.add_node("response_generation_node", response_generation_node)
    workflow.add_node("end_node", end_node)
    
    # Set entry point
    workflow.set_entry_point("task_analysis_node")
    
    # Add edges
    workflow.add_edge(START, "task_analysis_node")
    workflow.add_edge("task_analysis_node", "database_operation_node")
    workflow.add_edge("database_operation_node", "response_generation_node")
    workflow.add_edge("response_generation_node", "end_node")
    workflow.add_edge("end_node", END)
    
    return workflow

# Initialize the workflow
task_manager_graph = create_task_manager_workflow().compile(checkpointer=MemorySaver())
