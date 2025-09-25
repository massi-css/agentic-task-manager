"""Database operation node for the workflow."""

import uuid
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command
from copilotkit.langgraph import copilotkit_emit_state

from nodes.state import TaskManagerState
from task_database import task_db


async def database_operation_node(state: TaskManagerState, config: RunnableConfig) -> Command:
    """Execute the database operation based on the analyzed request"""

    operation = state.get("operation", "unknown")
    parameters = state.get("parameters", {})

    # Add log entry
    state["tool_logs"].append({
        "id": str(uuid.uuid4()),
        "message": "Executing operation",
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
        print(f"Database operation failed: {str(e)}")
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
            print(f"Failed to disconnect database: {str(disconnect_error)}")
            
        raise e