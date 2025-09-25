"""Workflow builder utilities."""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from nodes import (
    task_analysis_node,
    database_operation_node,
    response_generation_node,
    end_node,
    TaskManagerState
)


def decide_after_analysis(state: TaskManagerState) -> str:
    """Decide next step after task analysis"""
    operation = state.get("operation")
    
    if not operation or operation == "UNKNOWN":
        return "response_generation_node"
    
    if operation in ["BULK_ADD", "BULK_UPDATE", "BULK_DELETE"]:
        return "database_operation_node"
    
    return "database_operation_node"


def decide_after_database(state: TaskManagerState) -> str:
    """Decide next step after database operation"""
    db_result = state.get("db_result", {})
    operation = state.get("operation")
    
    if not db_result.get("success", False):
        error_type = db_result.get("error_type")
        retry_count = state.get("retry_count", 0)
        
        if error_type == "database_failure" and retry_count < 1:
            state["retry_count"] = retry_count + 1
            return "database_operation_node"
    
    if operation == "SUMMARIZE_TASKS" and db_result.get("success"):
        pass
    
    if operation in ["ADD_TASK", "UPDATE_TASK", "DELETE_TASK", "MARK_DONE"] and db_result.get("success"):
        pass
    
    return "response_generation_node"


def decide_after_response(state: TaskManagerState) -> str:
    """Decide if workflow should continue or end"""
    db_result = state.get("db_result", {})
    operation = state.get("operation")
    
    if not db_result.get("success", False) and operation not in ["UNKNOWN"]:
        error_type = db_result.get("error_type")
        
        if error_type == "analysis_failure":
            pass
    
    if operation == "GET_TASKS" and db_result.get("success"):
        tasks = db_result.get("tasks", [])
        pass
    
    return "end_node"


def create_task_manager_workflow() -> StateGraph:
    """Create and configure the task manager workflow graph with conditional edges"""
    
    workflow = StateGraph(TaskManagerState)
    
    workflow.add_node("task_analysis_node", task_analysis_node)
    workflow.add_node("database_operation_node", database_operation_node)
    workflow.add_node("response_generation_node", response_generation_node)
    workflow.add_node("end_node", end_node)
    
    workflow.set_entry_point("task_analysis_node")
    
    workflow.add_conditional_edges(
        "task_analysis_node",
        decide_after_analysis,
        {
            "database_operation_node": "database_operation_node",
            "response_generation_node": "response_generation_node"
        }
    )
    
    workflow.add_conditional_edges(
        "database_operation_node", 
        decide_after_database,
        {
            "database_operation_node": "database_operation_node",  
            "response_generation_node": "response_generation_node"
        }
    )
    
    workflow.add_conditional_edges(
        "response_generation_node",
        decide_after_response, 
        {
            "end_node": "end_node",
            "task_analysis_node": "task_analysis_node"
        }
    )
    
    workflow.add_edge("end_node", END)
    
    return workflow


def create_compiled_workflow():
    """Create and compile the workflow with memory"""
    return create_task_manager_workflow().compile(checkpointer=MemorySaver())