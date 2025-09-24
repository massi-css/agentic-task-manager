"""State definition for the task manager agent."""

from typing import Dict, List, Any, Optional
from langchain_core.messages import BaseMessage
from copilotkit import CopilotKitState


class TaskManagerState(CopilotKitState):
    """State for the task manager agent"""
    messages: List[BaseMessage] = []
    tool_logs: List[Dict[str, Any]] = []
    operation: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    db_result: Optional[Dict[str, Any]] = None
    final_response: Optional[str] = None