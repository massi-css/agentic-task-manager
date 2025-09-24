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


def create_compiled_workflow():
    """Create and compile the workflow with memory"""
    return create_task_manager_workflow().compile(checkpointer=MemorySaver())