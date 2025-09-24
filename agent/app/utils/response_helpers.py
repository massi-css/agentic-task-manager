"""Response generation helper functions."""

import json
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage

from utils.llm_model import get_llm_model
from utils.prompts import TASK_SUMMARIZER_PROMPT, TASK_EXECUTOR_PROMPT


async def generate_task_summary_response(summary_data: Dict[str, Any], config: RunnableConfig) -> str:
    """Generate natural language summary of tasks"""
    try:
        model = get_llm_model(temperature=0.3)
        
        summary_prompt = f"""
        {TASK_SUMMARIZER_PROMPT}
        
        Task Summary Data:
        {json.dumps(summary_data, default=str, indent=2)}
        
        Generate a helpful summary response for the user.
        """
        
        response = await model.ainvoke([HumanMessage(content=summary_prompt)], config)
        return response.content.strip()
        
    except Exception as e:
        print(f"Failed to generate task summary with LLM: {str(e)}")
        # Fallback to simple summary
        return _generate_fallback_summary(summary_data)


async def generate_standard_response(operation: str, result: Dict[str, Any], config: RunnableConfig) -> str:
    """Generate standard response for non-summary operations"""
    try:
        model = get_llm_model(temperature=0.3)
        
        response_prompt = f"""
        {TASK_EXECUTOR_PROMPT}
        
        Operation: {operation}
        Result: {json.dumps(result, default=str, indent=2)}
        
        Generate a natural, helpful response for the user.
        """
        
        response = await model.ainvoke([HumanMessage(content=response_prompt)], config)
        return response.content.strip()
        
    except Exception as e:
        print(f"Failed to generate standard response with LLM: {str(e)}")
        # Fallback to simple response
        return _generate_fallback_response(result)


def _generate_fallback_summary(summary_data: Dict[str, Any]) -> str:
    """Generate a simple fallback summary when LLM fails"""
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


def _generate_fallback_response(result: Dict[str, Any]) -> str:
    """Generate a simple fallback response when LLM fails"""
    if result.get("success"):
        return result.get("message", "Operation completed successfully!")
    else:
        return f"Sorry, {result.get('message', 'the operation failed')}."